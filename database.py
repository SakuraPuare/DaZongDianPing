from typing import Union, Iterable

from sqlalchemy import Column, Integer, String, Text, create_engine, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


class Shop(Base):
    __tablename__ = "shop"

    id: int = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    name: str = Column(String(255), nullable=False, comment='店铺名称')
    url: str = Column(String(511), nullable=False, comment='店铺链接')
    category: str = Column(String(255), nullable=False, comment='店铺分类')
    region: str = Column(String(255), nullable=False, comment='店铺区域')
    star: float = Column(Float, nullable=False, comment='店铺星级')
    comment: int = Column(Integer, nullable=False, comment='店铺评论数')
    price: int = Column(Integer, nullable=False, comment='店铺人均价格')
    pic_url: str = Column(String(1023), nullable=False, comment='店铺图片链接')
    recommend: str = Column(String(255), nullable=False, comment='店铺推荐菜')
    promotion: int = Column(Integer, nullable=False, comment='店铺优惠数量')
    promotion_info: str = Column(Text, nullable=False, comment='店铺优惠信息')

    def __repr__(self):
        return f'<Shop {self.name}>'


class Database:
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url, echo=True)
        self.session = sessionmaker(bind=self.engine)()

    def init(self) -> None:
        self.create_all_table()

    def create_all_table(self) -> None:
        Base.metadata.create_all(self.engine)

    def insert_shop(self, shop: Union[Iterable[Shop], Shop]) -> None:
        if isinstance(shop, list):
            self.session.add_all(shop)
        else:
            self.session.add(shop)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.close()

    def close(self) -> None:
        self.session.close()
        self.engine.dispose()


if __name__ == '__main__':
    db = Database('mysql+pymysql://root:test@localhost:3306/dianping?charset=utf8mb4')
    db.create_all_table()

    db.close()
