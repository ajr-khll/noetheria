from models import ChatSession
sessions = ChatSession.query.all()
for s in sessions:
    print(s.id)