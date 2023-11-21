from agents.db.data_model import AgentConfigModel
from agents.db.session import with_session


@with_session
def get_from_db(session, key):
    record = session.query(AgentConfigModel).filter_by(key=key).first()
    if record:
        return record.agent_config


@with_session
def add_or_update_to_db(
    session,
    key,
    agent_config,
):
    record = session.query(AgentConfigModel).filter_by(key=key).first()
    if not record:
        new_record = AgentConfigModel(
            key=key,
            agent_config=agent_config,
        )
        session.add(new_record)
    else:
        record.agent_config = agent_config
    return True


@with_session
def delete_from_db(session, key):
    record = session.query(AgentConfigModel).filter_by(key=key).first()
    if record:
        session.delete(record)
    return True


@with_session
def exists_in_db(session, key):
    record = session.query(AgentConfigModel).filter_by(key=key).first()
    if record:
        return True
    return False


@with_session
def list_all_keys(session):
    records = session.query(AgentConfigModel).all()
    res = []
    for record in records:
        res.append(record.key)
    return res
