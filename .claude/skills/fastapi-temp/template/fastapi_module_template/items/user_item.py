#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
from pydantic import BaseModel


class UserItem(BaseModel):
    username: str
    password: str


def main():
    pass


if __name__ == "__main__":
    main()
