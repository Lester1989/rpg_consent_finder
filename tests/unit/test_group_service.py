from models.db_models import User, RPGGroup
from services.group_service import (
    create_new_group,
    join_group,
    leave_group,
    fetch_group_users,
    get_group_by_id
)

def test_create_new_group(session):
    user = User(id_name="test", nickname="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    group = create_new_group(user, session=session)
    
    assert group.id is not None
    assert group.gm_user_id == user.id
    assert group.name == "test-user-group"
    assert group.invite_code is not None
    
    # Verify GM is a member
    members = fetch_group_users(group, session=session)
    assert len(members) == 1
    assert members[0].id == user.id

def test_join_and_leave_group(session):
    gm = User(id_name="gm", nickname="GM")
    player = User(id_name="player", nickname="Player")
    session.add(gm)
    session.add(player)
    session.commit()
    session.refresh(gm)
    session.refresh(player)
    
    group = create_new_group(gm, session=session)
    
    # Join
    joined_group = join_group(group.invite_code, player, session=session)
    assert joined_group is not None
    assert joined_group.id == group.id
    
    # Check membership
    members = fetch_group_users(group, session=session)
    assert len(members) == 2
    member_ids = {m.id for m in members}
    assert gm.id in member_ids
    assert player.id in member_ids
    
    # Leave
    leave_group(group, player, session=session)
    
    # Check membership
    members = fetch_group_users(group, session=session)
    assert len(members) == 1
    assert members[0].id == gm.id
