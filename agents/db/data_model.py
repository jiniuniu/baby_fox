from sqlalchemy import Column, Integer, String

from agents.db.base import Base


class AgentConfigModel(Base):
    __tablename__ = "agent_config"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    key = Column(String, comment="agent的key")
    agent_config = Column(String, comment="agent的配置信息")

    def __repr__(self):
        return f"<AgentConfig(id='{self.id}', agent_key='{self.key}', config_info='{self.agent_config}')>"
