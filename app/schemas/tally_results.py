from pydantic import BaseModel

class TallyResultBase(BaseModel):
    company_data: list
    bank_data: list


class TallyResultCreate(TallyResultBase):
    pass


class TallyResultResponse(TallyResultBase):
    id: int

    class Config:
        from_attributes = True