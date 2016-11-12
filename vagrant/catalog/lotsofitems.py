from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemcatalogusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

session.query(Category).delete()
session.query(Item).delete()
session.query(User).delete()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(name="Fruit")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="Apple", description="Juicy fruit", category=category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1, name="Orange", description="Vitamin C", category=category1)

session.add(item2)
session.commit()

category2 = Category(name="Veggie")

session.add(category2)
session.commit()

item3 = Item(user_id=1, name="Spinach", description="Iron", category=category2)

session.add(item3)
session.commit()


item4 = Item(user_id=1, name="Broccoli", description="Good Fiber", category=category2)

session.add(item4)
session.commit()
