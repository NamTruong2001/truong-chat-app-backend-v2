from datetime import datetime
from enum import Enum
from typing import Union

from beanie import PydanticObjectId

# from .enums import UserMessageType
from pydantic import BaseModel, Field

from model.mongo import Attachment
from enums import UserMessageType
from enums import SystemMessageType


# class MessageType(str, Enum):
#     TEXT = "text"
#     IMAGE = "image"
#     VIDEO = "video"
#     FILE = "file"


class UserMessageRequest(BaseModel):
    conversation_id: str
    sender_id: str
    type: UserMessageType
    content: str
    attachment: Union[None, Attachment] = None

    class Config:
        use_enum_value = True


class SystemMessageRequest(BaseModel):
    conversation_id: str
    type: SystemMessageType
    attachment: Union[None, Attachment] = None

    class Config:
        use_enum_value = True


class MessageInResponse(UserMessageRequest):
    id: str
    created_at: datetime


class SystemMessageInResponse(SystemMessageRequest):
    id: str
    created_at: datetime
    system_content: dict


class GetConversationMessagesWithPage(BaseModel):
    conversation_id: str
    page: int = Field(gt=0, default=1)
    page_size: int = Field(gt=0, default=30)


class UserTemporaryInfo(BaseModel):
    user_id: PydanticObjectId
    username: str


class SystemMessageContent(BaseModel):
    pass


class UserSysAction(str, Enum):
    leave_conversation = "leave_conversation"
    join_conversation = "join_conversation"
    remove_participant = "remove_participant"
    add_participant = "add_participant"
    test = "test"


class UserLeaveConversation(SystemMessageContent):
    user_id: UserTemporaryInfo
    action: UserSysAction = UserSysAction.leave_conversation


class TestAction(SystemMessageContent):
    action: UserSysAction = UserSysAction.test


class UserJoinConversation(SystemMessageContent):
    user: UserTemporaryInfo
    action: UserSysAction = UserSysAction.join_conversation


class UserAddedToConversation(SystemMessageContent):
    users: list[UserTemporaryInfo]
    action: UserSysAction = UserSysAction.add_participant


class UserRemovedFromConversation(SystemMessageContent):
    users: list[UserTemporaryInfo]
    action: UserSysAction = UserSysAction.remove_participant
