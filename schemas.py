from datetime import date

from dateutil import relativedelta
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, Relationship, Column, VARCHAR

from date_utils import DateUtils

pwd_context = CryptContext(schemes=["bcrypt"])


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    username: str = Field(sa_column=Column(VARCHAR, unique=True, index=True))
    password_hash: str = ""

    def set_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class UserOutput(SQLModel):
    id: int
    username: str


class BalanceMovimientoInput(SQLModel):
    importe: float
    concepto: str
    tipo: str
    balance_id: int = Field(foreign_key="balance.id")
    entity: str | None
    entity_id: int
    categoria_id: int | None = Field(foreign_key="gasto_categoria.id")


class BalanceMovimiento(BalanceMovimientoInput, table=True):
    __tablename__ = "balance_movimiento"

    id: int | None = Field(primary_key=True, default=None)
    balance: "Balance" = Relationship(back_populates="movimientos")
    categoria: "GastoCategoria" = Relationship(back_populates="movimientos")


class BalanceInput(SQLModel):
    periodo: str

    class Config:
        schema_extra = {
            "example": {
                "periodo": date.today().strftime("%Y%m")
            }
        }


class Balance(BalanceInput, table=True):
    __tablename__ = "balance"

    id: int | None = Field(primary_key=True, default=None)
    movimientos: list[BalanceMovimiento] = Relationship(back_populates="balance",
                                                        sa_relationship_kwargs={"cascade": "delete"})
    importe_total_ingresos: float = 0
    importe_total_egresos: float = 0
    importe_saldo: float = 0


class BalanceOutput(SQLModel):
    id: int
    periodo: str
    importe_total_ingresos: float = 0
    importe_total_egresos: float = 0
    importe_saldo: float = 0
    # movimientos: list


class DebitoAutomaticoInput(SQLModel):
    importe: float
    concepto: str
    periodo_inicio: str
    periodo_fin: str | None = None
    activo: bool = True
    tarjeta_id: int = Field(foreign_key="tarjeta.id")
    categoria_id: int = Field(foreign_key="gasto_categoria.id")

    class Config:
        schema_extra = {
            "example": {
                "importe": 3999.99,
                "concepto": "debito prueba",
                "periodo_inicio": date.today().strftime("%Y%m"),
                "periodo_fin": "",
                "activo": 1,
                "tarjeta_id": 1,
                "categoria_id": 6
            }
        }


class DebitoAutomatico(DebitoAutomaticoInput, table=True):
    __tablename__ = "debito_automatico"

    id: int | None = Field(primary_key=True, default=None)

    tarjeta: "Tarjeta" = Relationship(back_populates="debitos_automaticos")
    categoria: "GastoCategoria" = Relationship(back_populates="debitos_automaticos")


class GastoExtraInput(SQLModel):
    importe: float
    concepto: str
    fecha: str
    categoria_id: int = Field(foreign_key="gasto_categoria.id")

    class Config:
        schema_extra = {
            "example": {
                "importe": 2999.99,
                "concepto": "gasto extra prueba",
                "fecha": date.today().strftime("%Y%m%d"),
                "categoria_id": 1
            }
        }


class GastoExtra(GastoExtraInput, table=True):
    __tablename__ = "gasto_extra"

    id: int | None = Field(primary_key=True, default=None)

    categoria: "GastoCategoria" = Relationship(back_populates="gastos_extras")


class GastoFijoInput(SQLModel):
    importe: float
    concepto: str
    periodo_inicio: str
    periodo_fin: str | None = None
    activo: bool = True
    categoria_id: int = Field(foreign_key="gasto_categoria.id")

    class Config:
        schema_extra = {
            "example": {
                "importe": 1999.99,
                "concepto": "gasto fijo prueba",
                "periodo_inicio": date.today().strftime("%Y%m"),
                "periodo_fin": "",
                "activo": 1,
                "categoria_id": 1
            }
        }


class GastoFijo(GastoFijoInput, table=True):
    __tablename__ = "gasto_fijo"

    id: int | None = Field(primary_key=True, default=None)

    categoria: "GastoCategoria" = Relationship(back_populates="gastos_fijos")


class GastoTarjetaInput(SQLModel):
    fecha: str
    concepto: str
    cant_cuotas: int
    importe_total: float | None = None
    importe: float | None = None
    periodo_inicio: str | None = None
    periodo_fin: str | None = None
    categoria_id: int = Field(foreign_key="gasto_categoria.id")
    tarjeta_id: int = Field(foreign_key="tarjeta.id")

    class Config:
        schema_extra = {
            "example": {
                "fecha": date.today().strftime("%Y%m%d"),
                "concepto": "credito 3 cuotas prueba",
                "importe_total": 3000,
                "cant_cuotas": 3,
                "tarjeta_id": 1,
                "categoria_id": 6
            }
        }


class GastoTarjeta(GastoTarjetaInput, table=True):
    __tablename__ = "gasto_tarjeta"

    id: int | None = Field(primary_key=True, default=None)
    categoria: "GastoCategoria" = Relationship(back_populates="gastos_tarjetas")
    tarjeta: "Tarjeta" = Relationship(back_populates="consumos")

    @property
    def consumo_activo(self):
        current_period = DateUtils.get_current_month_period()
        return self.periodo_fin >= current_period

    @consumo_activo.setter
    def consumo_activo(self, value):
        self.consumo_activo = value

    @property
    def nro_cuota(self):
        periodo_actual = date.today()
        periodo_inicio = DateUtils.periodo_to_date_object(self.periodo_inicio)
        if self.consumo_activo == False or periodo_actual < periodo_inicio:
            return None
        dif_date = relativedelta.relativedelta(periodo_actual, periodo_inicio)
        nro_cuota = 1
        if dif_date.years > 0:
            nro_cuota = 12 * dif_date.years
        nro_cuota = nro_cuota + dif_date.months
        return nro_cuota

    @nro_cuota.setter
    def nro_cuota(self, value):
        self.nro_cuota = value


class IngresoExtraInput(SQLModel):
    importe: float
    concepto: str
    fecha: str

    class Config:
        schema_extra = {
            "example": {
                "fecha": date.today().strftime("%Y%m%d"),
                "concepto": "prueba ingreso extra",
                "importe": 30000,
            }
        }


class IngresoExtra(IngresoExtraInput, table=True):
    __tablename__ = "ingreso_extra"

    id: int | None = Field(primary_key=True, default=None)


class IngresoFijoInput(SQLModel):
    importe: float
    concepto: str
    activo: bool = True

    class Config:
        schema_extra = {
            "example": {
                "importe": 100000.00,
                "concepto": "prueba ingreso fijo concepto",
                "activo": 1,
            }
        }


class IngresoFijo(IngresoFijoInput, table=True):
    __tablename__ = "ingreso_fijo"

    id: int | None = Field(primary_key=True, default=None)


class TarjetaInput(SQLModel):
    nombre: str
    banco: str
    activo: bool = True

    class Config:
        schema_extra = {
            "example": {
                "nombre": "prueba tarjeta nombre",
                "banco": "prueba tarjeta banco",
                "activo": 1,
            }
        }


class Tarjeta(TarjetaInput, table=True):
    __tablename__ = "tarjeta"

    id: int | None = Field(primary_key=True, default=None)
    debitos_automaticos: list[DebitoAutomatico] = Relationship(back_populates="tarjeta")
    consumos: list[GastoTarjeta] = Relationship(back_populates="tarjeta")

    @property
    def label(self):
        return f"{self.nombre} {self.banco}"

    @label.setter
    def label(self, value):
        self.label = value


class GastoCategoriaInput(SQLModel):
    nombre: str

    class Config:
        schema_extra = {
            "example": {
                "nombre": "prueba categoria nombre"
            }
        }


class GastoCategoria(GastoCategoriaInput, table=True):
    __tablename__ = "gasto_categoria"

    id: int | None = Field(primary_key=True, default=None)
    debitos_automaticos: list[DebitoAutomatico] = Relationship(back_populates="categoria")
    gastos_extras: list[GastoExtra] = Relationship(back_populates="categoria")
    gastos_fijos: list[GastoFijo] = Relationship(back_populates="categoria")
    gastos_tarjetas: list[GastoTarjeta] = Relationship(back_populates="categoria")
    movimientos: list[BalanceMovimiento] = Relationship(back_populates="categoria")

    @property
    def label(self):
        return f"{self.nombre}"

    @label.setter
    def label(self, value):
        self.label = value


class GastoTarjetaOutput(SQLModel):
    id: int
    fecha: str
    concepto: str
    importe_total: float
    nro_cuota: int | None
    cant_cuotas: int
    importe: float
    periodo_inicio: str
    periodo_fin: str
    consumo_activo: bool
    tarjeta: Tarjeta
    categoria: GastoCategoria


class GastoFijoOutput(SQLModel):
    id: int
    periodo_inicio: str
    periodo_fin: str | None
    importe: float
    concepto: str
    activo: bool
    categoria: GastoCategoria


class TarjetaOutput(SQLModel):
    id: int
    nombre: str
    banco: str
    label: str


class GastoCategoriaOutput(SQLModel):
    id: int
    nombre: str
    label: str
