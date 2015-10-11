from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Cities, Base, Destinations

engine = create_engine('postgresql+psycopg2:///cities')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

# Drop all tables and recreate
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# http://www.japan-guide.com/

# Tokyo
city1 = Cities(name="Tokyo", image='http://www.japan-guide.com/g10/destination_tokyo_top.jpg')

session.add(city1)
session.commit()

destination1 = Destinations(name="Tsukiji Fish Market", description="A large wholesale market for fish, fruits and vegetables in central Tokyo",
                     price="Free", cities=city1, image='http://www.japan-guide.com/g2/3021_01.jpg')

session.add(destination1)
session.commit()


destination2 = Destinations(name="Akihabara", description="A district in central Tokyo that is famous for its many electronics shops",
                     price="Free", cities=city1, image='http://www.japan-guide.com/g9/3003_01.jpg')

session.add(destination2)
session.commit()

destination3 = Destinations(name="Koishikawa Korakuen", description="One of Tokyo's oldest and best Japanese gardens.",
                     price="300", cities=city1, image='http://www.japan-guide.com/g3/3034_05.jpg')

session.add(destination3)
session.commit()

destination4 = Destinations(name="Imperial Palace East Gardens", description="A part of the inner palace area and are open to the public.",
                     price="Free", cities=city1, image='http://www.japan-guide.com/g3/3018_13.jpg')

session.add(destination4)
session.commit()


city2 = Cities(name="Yokohama", image='http://www.japan-guide.com/g10/destination_yokohama_top.jpg')

session.add(city2)
session.commit()

destination1 = Destinations(name="Sankeien Garden", description="A spacious Japanese style garden which exhibits a number of historic buildings from across Japan.",
                     price="500", cities=city2, image='http://www.japan-guide.com/g2/3205_01.jpg')

session.add(destination1)
session.commit()


destination2 = Destinations(name="Minato Mirai 21", description="Minato Mirai 21 is a seaside urban area in central Yokohama whose name means harbor of the future",
                     price="free", cities=city2, image='http://www.japan-guide.com/g2/3200_01.jpg')

session.add(destination2)
session.commit()

destination3 = Destinations(name="Zoorasia", description="One of Japan's newest, largest and best kept zoos",
                     price="800", cities=city2, image='http://www.japan-guide.com/g2/3209_01.jpg')

session.add(destination3)
session.commit()

destination4 = Destinations(name="Ramen Museum", description="The Shinyokohama Raumen Museum is a unique museum about ramen",
                     price="300", cities=city2, image='http://www.japan-guide.com/g2/3202_01.jpg')

session.add(destination4)
session.commit()


city3 = Cities(name="Kawasaki", image='http://www.japan-guide.com/g10/destination_kawasaki_top.jpg')

session.add(city3)
session.commit()

destination1 = Destinations(name="Fujiko F. Fujio Museum", description="Doraemon Museum, is a fanciful art museum found in the suburbs of Kawasaki.",
                     price="1000", cities=city3, image='http://www.japan-guide.com/g7/3252_04.jpg')

session.add(destination1)
session.commit()


destination2 = Destinations(name="Nihon Minkaen Open Air Museum", description="The museum is home to 25 preserved buildings from the Edo Period",
                     price="500", cities=city3, image='http://www.japan-guide.com/g7/3253_01.jpg')

session.add(destination2)
session.commit()

destination3 = Destinations(name="Kawasaki Daishi Temple", description="A prominent temple founded in 1128 toward the end of the Heian Period ",
                     price="Free", cities=city3, image='http://www.japan-guide.com/g7/3254_01.jpg')

session.add(destination3)
session.commit()



# destination4 = Destinations(name="", description="",
#                      price="", cities=city1, image='')

# session.add(destination4)
# session.commit()
# =================================
# city = Cities(name="", image='')

# session.add(city)
# session.commit()

# destination1 = Destinations(name="", description="",
#                      price="", cities=city, image='')

# session.add(destination1)
# session.commit()


# destination2 = Destinations(name="", description="",
#                      price="", cities=city, image='')

# session.add(destination2)
# session.commit()

# destination3 = Destinations(name="", description="",
#                      price="", cities=city, image='')

# session.add(destination3)
# session.commit()

# destination4 = Destinations(name="", description="",
#                      price="", cities=city, image='')

# session.add(destination4)
# session.commit()