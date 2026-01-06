from sqlalchemy import Column, Integer, String, Boolean
from app.database.session import Base

class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50))
    vehicle_code = Column(String(50), unique=True)
    vin = Column(String(20), unique=True)
    phase = Column(String(20))
    configuration = Column(String(100))
    chip_platform = Column(String(50))
    wheel_size = Column(Integer)
    has_data_device = Column(Boolean)
    current_status = Column(String(20))