from dataclasses import dataclass, field
from datetime import datetime

@dataclass #dataclass essentially enables us to hard code the variable types and go away from the pythonic way of dynamic type casting
class Notification:
    _id: str
    title: str
    content:str
    dateSent: datetime = None
    dateCreated: datetime = None
    language: str = "English"
    ratingImportance: int =0
    tags: list[str] = field(default_factory=list)
    comment: str = "None"
    status: str = "Draft"
    

@dataclass
class User:
    _id: str
    email: str
    password: str
    notifications: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    surveys: list[str] = field(default_factory=list)


@dataclass
class Survey:
    _id: str
    title: str
    
    content: str
    questions: list[str] = field(default_factory=list)

@dataclass
class OpenSurvey:
    contact: str
    questions: list[str] = field(default_factory=list)
    responses: list[str] = field(default_factory=list)
    

@dataclass
class Question:
    _id: str
    title: str
    content: str

@dataclass
class Contact:
    _id: str
    name: str
    phone:str
    gender:str
    age: int
    kids:int
    education: str  
    village: str        #should be category
    

@dataclass
class ScheduledMessage:
    _id:str
    gender:str
    age: int
    kids:int
    education: str  
    village: str  
    messageId: str
    date: datetime 
    nors: str

@dataclass
class SentMessage:
    _id: str
    project: str
    date: datetime
    response : object
    