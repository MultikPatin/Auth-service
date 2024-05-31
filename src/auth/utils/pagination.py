from http import HTTPStatus
from typing import Annotated, Any

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field


class PaginatedMixin(BaseModel):
    count: int = Field(
        description="Количество строк в таблице",
        example=356,
    )
    total_pages: int = Field(
        description="Количество страниц с заданным 'page_size' в таблице",
        example=20,
    )
    prev: int | None = Field(
        description="Номер предыдущей страницы",
        example=1,
    )
    next: int | None = Field(
        description="Номер следующей страницы",
        example=3,
    )

    class Meta:
        abstract = True


class PaginatedData(PaginatedMixin):
    results: Any


class Paginator:
    __count: int

    def __init__(self, page_number: int, page_size: int):
        self.__page_number = page_number
        self.__page_size = page_size

    async def __call__(self, service, method, **kwargs) -> PaginatedData:
        try:
            self.__count = await service.count(**kwargs)
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"{e}: Error getting the number of records",
            ) from None
        kwargs.update(self._validate())
        attr = getattr(service, method)
        models = await attr(**kwargs)
        if not models:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="history not found"
            )
        return PaginatedData(**self._get_result_params().dict(), results=models)

    def _validate(self) -> dict:
        if self.__page_number > 1:
            total = (self.__page_number - 1) * self.__page_size + 1
            if total > self.__count:
                raise HTTPException(
                    status_code=400,
                    detail="Incorrect pagination parameters are set",
                )
        offset = (self.__page_number - 1) * self.__page_size
        limit = self.__page_size
        return {"limit": limit, "offset": offset}

    def _get_result_params(self) -> PaginatedMixin:
        prev = None
        next = None
        total_pages = self.__count // self.__page_size
        if self.__page_size * total_pages < self.__count:
            total_pages += 1
        if total_pages != 1:
            if self.__page_number > 1:
                prev = self.__page_number - 1
            if self.__page_number < total_pages:
                next = self.__page_number + 1
        return PaginatedMixin(
            count=self.__count,
            total_pages=total_pages,
            prev=prev,
            next=next,
        )


def get_paginator(
    page_number: Annotated[
        int,
        Query(
            alias="page_number",
            title="Page number",
            description="The number of the page to get",
            ge=1,
            le=100,
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            alias="page_size",
            title="Page size",
            description="The size of the page to get",
            ge=1,
            le=100,
        ),
    ] = 50,
) -> Paginator:
    return Paginator(page_number, page_size)
