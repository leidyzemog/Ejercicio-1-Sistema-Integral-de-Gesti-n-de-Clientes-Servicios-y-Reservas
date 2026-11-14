#Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas
#Desarrollado por: Leidy johana Gomez, karen liceth acosta, Daniel Ayala.

# Este programa es un sistema integral de gestión de clientes, servicios y reservas. Permite a los usuarios registrar clientes, gestionar servicios ofrecidos y realizar reservas de manera eficiente.
# Bienvenido al sistema
print("BIENVENIDO AL SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS")

input("Presione Enter para continuar...")

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re


# ==========================================================
# CONFIGURACIÓN DEL ARCHIVO DE REGISTRO
# ==========================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ==========================================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================================

class ErrorSistema(Exception):
    """Excepción general del sistema."""


class DatosInvalidosError(ErrorSistema):
    """Se presenta cuando los datos ingresados no son válidos."""


class ClienteNoEncontradoError(ErrorSistema):
    """Se presenta cuando no existe el cliente solicitado."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se presenta cuando un servicio no está disponible."""


class ReservaNoPermitidaError(ErrorSistema):
    """Se presenta cuando una operación de reserva no está permitida."""


class CalculoCostoError(ErrorSistema):
    """Se presenta cuando ocurre un error al calcular un costo."""


# ==========================================================
# CLASE ABSTRACTA ENTIDAD
# ==========================================================

class Entidad(ABC):

    contador = 0

    def __init__(self):
        Entidad.contador += 1
        self._identificador = Entidad.contador

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def obtener_resumen(self):
        pass


# ==========================================================
# CLASE CLIENTE
# ==========================================================

class Cliente(Entidad):

    def __init__(self, nombre, correo, telefono):
        super().__init__()
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatosInvalidosError("El nombre no puede estar vacío.")
        if not all(letra.isalpha() or letra.isspace() for letra in valor):
            raise DatosInvalidosError("El nombre solo debe contener letras y espacios.")
        self.__nombre = valor.strip().title()

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        patron = r"^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")
        self.__correo = valor.strip().lower()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) != 10:
            raise DatosInvalidosError("El teléfono debe contener exactamente 10 dígitos.")
        self.__telefono = str(valor)

    def obtener_resumen(self):
        return (
            f"Cliente #{self.identificador}: {self.nombre} | "
            f"{self.correo} | {self.telefono}"
        )


# ==========================================================
# CLASE ABSTRACTA SERVICIO
# ==========================================================

class Servicio(Entidad, ABC):

    def __init__(self, nombre, tarifa_base):
        super().__init__()
        if not nombre or not isinstance(nombre, str):
            raise DatosInvalidosError("El servicio debe tener un nombre.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa base debe ser mayor que cero.")
        self.nombre = nombre
        self.tarifa_base = float(tarifa_base)
        self.activo = True

    @abstractmethod
    def validar_parametros(self, **parametros):
        pass

    @abstractmethod
    def calcular_costo(self, **parametros):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    def aplicar_impuestos_descuento(self, subtotal, impuesto=0.19, descuento=0):
        if not 0 <= impuesto <= 1:
            raise CalculoCostoError("El impuesto debe estar entre 0 y 1.")
        if not 0 <= descuento <= 1:
            raise CalculoCostoError("El descuento debe estar entre 0 y 1.")
        total = subtotal * (1 + impuesto) * (1 - descuento)
        return round(total, 2)
        
    def calcular_costo_sobrecargado(self, *args, **kwargs):
        # Python no tiene sobrecarga nativa; se simula según los argumentos recibidos
        cantidad_args = len(args)  # Cuenta los argumentos posicionales

        if cantidad_args == 0:  # Variante A: solo parámetros nombrados
            return self.calcular_costo(**kwargs)  # Usa el cálculo propio del servicio

        if cantidad_args == 1 and isinstance(args[0], dict):  # Variante B: un diccionario
            return self.calcular_costo(**args[0])  # Desempaqueta el diccionario

        todos_numeros = all(  # Verifica que todos los argumentos sean numéricos
            isinstance(a, (int, float)) and not isinstance(a, bool) for a in args
        )
        if cantidad_args in (1, 2, 3) and todos_numeros:  # Variante C: (subtotal, impuesto, descuento)
            return self.aplicar_impuestos_descuento(*args)  # Usa el método base

        raise CalculoCostoError(  # Cualquier otra combinación es inválida
            "Combinación de argumentos no soportada para calcular el costo."
        )
    def obtener_resumen(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"Servicio #{self.identificador}: {self.nombre} | ${self.tarifa_base:,.2f} | {estado}"


# ==========================================================
# SERVICIO 1: RESERVA DE SALAS
# ==========================================================

class ReservaSala(Servicio):

    def __init__(self, nombre, tarifa_base, capacidad):
        super().__init__(nombre, tarifa_base)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidosError("La capacidad debe ser un número entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, **parametros):
        horas = parametros.get("horas", 1)
        asistentes = parametros.get("asistentes", 1)
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise DatosInvalidosError("Las horas deben ser mayores que cero.")
        if not isinstance(asistentes, int) or asistentes <= 0:
            raise DatosInvalidosError("Los asistentes deben ser un entero positivo.")
        if asistentes > self.capacidad:
            raise ServicioNoDisponibleError(
                f"La sala admite máximo {self.capacidad} asistentes."
            )

    def calcular_costo(self, horas=1, asistentes=1, impuesto=0.19, descuento=0):
        self.validar_parametros(horas=horas, asistentes=asistentes)
        subtotal = self.tarifa_base * horas
        return self.aplicar_impuestos_descuento(subtotal, impuesto, descuento)

    def describir_servicio(self):
        return f"Sala para reuniones con capacidad máxima de {self.capacidad} personas."


# ==========================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# ==========================================================

class AlquilerEquipo(Servicio):

    def __init__(self, nombre, tarifa_base, unidades_disponibles):
        super().__init__(nombre, tarifa_base)
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise DatosInvalidosError("Las unidades disponibles no pueden ser negativas.")
        self.unidades_disponibles = unidades_disponibles

    def validar_parametros(self, **parametros):
        cantidad = parametros.get("cantidad", 1)
        dias = parametros.get("dias", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise DatosInvalidosError("La cantidad debe ser un entero positivo.")
        if not isinstance(dias, int) or dias <= 0:
            raise DatosInvalidosError("Los días deben ser un entero positivo.")
        if cantidad > self.unidades_disponibles:
            raise ServicioNoDisponibleError(
                f"Solo hay {self.unidades_disponibles} unidades disponibles."
            )

    def calcular_costo(self, cantidad=1, dias=1, impuesto=0.19, descuento=0):
        self.validar_parametros(cantidad=cantidad, dias=dias)
        subtotal = self.tarifa_base * cantidad * dias
        return self.aplicar_impuestos_descuento(subtotal, impuesto, descuento)

    def describir_servicio(self):
        return f"Alquiler de equipos. Unidades disponibles: {self.unidades_disponibles}."


# ==========================================================
# SERVICIO 3: ASESORÍAS ESPECIALIZADAS
# ==========================================================

class AsesoriaEspecializada(Servicio):

    def __init__(self, nombre, tarifa_base, modalidad):
        super().__init__(nombre, tarifa_base)
        if modalidad not in ("virtual", "presencial"):
            raise DatosInvalidosError("La modalidad debe ser virtual o presencial.")
        self.modalidad = modalidad

    def validar_parametros(self, **parametros):
        horas = parametros.get("horas", 1)
        modalidad = parametros.get("modalidad", self.modalidad)
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise DatosInvalidosError("Las horas de asesoría deben ser mayores que cero.")
        if modalidad not in ("virtual", "presencial"):
            raise DatosInvalidosError("Modalidad no válida.")

    def calcular_costo(self, horas=1, modalidad=None, impuesto=0.19, descuento=0):
        modalidad_final = modalidad or self.modalidad
        self.validar_parametros(horas=horas, modalidad=modalidad_final)
        subtotal = self.tarifa_base * horas
        if modalidad_final == "presencial":
            subtotal += 20000
        return self.aplicar_impuestos_descuento(subtotal, impuesto, descuento)

    def describir_servicio(self):
        return f"Asesoría especializada en modalidad {self.modalidad}."


# ==========================================================
# CLASE RESERVA
# ==========================================================

class Reserva(Entidad):

    def __init__(self, cliente, servicio, duracion, parametros=None):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva debe estar asociada a un cliente.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva debe estar asociada a un servicio.")
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración debe ser mayor que cero.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.parametros = parametros or {}
        self.estado = "Pendiente"
        self.costo = None
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.activo:
            raise ServicioNoDisponibleError("El servicio está inactivo.")
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        if self.estado not in ("Pendiente", "Confirmada"):
            raise ReservaNoPermitidaError("No se puede cancelar una reserva procesada.")
        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self):
        if self.estado != "Confirmada":
            raise ReservaNoPermitidaError("La reserva debe estar confirmada para procesarse.")
        self.costo = self.servicio.calcular_costo(**self.parametros)
        self.estado = "Procesada"
        logging.info("Reserva %s procesada. Total: %s", self.identificador, self.costo)
        return self.costo

    def obtener_resumen(self):
        costo_texto = f"${self.costo:,.2f}" if self.costo is not None else "Pendiente de cálculo"
        return (
            f"Reserva #{self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Estado: {self.estado} | "
            f"Total: {costo_texto}"
        )


# ==========================================================
# CLASE PRINCIPAL DEL SISTEMA
# ==========================================================

class SistemaGestion:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, nombre, correo, telefono):
        cliente = Cliente(nombre, correo, telefono)
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.nombre)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El elemento no es un servicio válido.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.nombre)
        return servicio

    def buscar_cliente(self, identificador):
        for cliente in self.clientes:
            if cliente.identificador == identificador:
                return cliente
        raise ClienteNoEncontradoError("No se encontró el cliente solicitado.")

    def buscar_servicio(self, identificador):
        for servicio in self.servicios:
            if servicio.identificador == identificador:
                return servicio
        raise ServicioNoDisponibleError("No se encontró el servicio solicitado.")

    def crear_reserva(self, id_cliente, id_servicio, duracion, parametros=None):
        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        reserva = Reserva(cliente, servicio, duracion, parametros)
        self.reservas.append(reserva)
        logging.info("Reserva %s creada.", reserva.identificador)
        return reserva


# ==========================================================
# MANEJO GENERAL DE OPERACIONES Y EXCEPCIONES
# ==========================================================

def ejecutar_operacion(descripcion, operacion):
    print(f"\n>> {descripcion}")
    try:
        resultado = operacion()
    except ErrorSistema as error:
        print(f"Error controlado: {error}")
        logging.error("%s: %s", descripcion, error)
    except Exception as error:
        print(f"Error inesperado: {error}")
        logging.exception("Error inesperado durante: %s", descripcion)
    else:
        if resultado is not None:
            print(resultado)
        print("Operación realizada correctamente.")
    finally:
        print("Fin de la operación.")


# ==========================================================
# DATOS INICIALES DE SERVICIOS
# ==========================================================

sistema = SistemaGestion()


def cargar_servicios_iniciales():
    sistema.registrar_servicio(ReservaSala("Sala de reuniones", 50000, 20))
    sistema.registrar_servicio(AlquilerEquipo("Computador portátil", 30000, 8))
    sistema.registrar_servicio(AsesoriaEspecializada("Asesoría de software", 80000, "virtual"))


# ==========================================================
# SIMULACIÓN DE AL MENOS DIEZ OPERACIONES
# ==========================================================

def ejecutar_pruebas():
    print("\n========== SIMULACIÓN DE OPERACIONES ==========")
    sistema_pruebas = SistemaGestion()

    # 1. Registro válido de cliente
    ejecutar_operacion(
        "1. Registrar cliente válido",
        lambda: sistema_pruebas.registrar_cliente(
            "Ana Pérez", "ana@gmail.com", "3001234567"
        ).obtener_resumen()
    )

    # 2. Registro de otro cliente válido
    ejecutar_operacion(
        "2. Registrar segundo cliente",
        lambda: sistema_pruebas.registrar_cliente(
            "Carlos Ruiz", "carlos@gmail.com", "3101234567"
        ).obtener_resumen()
    )

    # 3. Intento de cliente con correo inválido y encadenamiento de excepción
    def cliente_invalido():
        try:
            return sistema_pruebas.registrar_cliente(
                "María López", "correo_invalido", "3201234567"
            )
        except DatosInvalidosError as error:
            raise ErrorSistema("No fue posible completar el registro del cliente.") from error

    ejecutar_operacion("3. Intentar registrar cliente con correo inválido", cliente_invalido)

    # 4. Intento de cliente con teléfono inválido
    ejecutar_operacion(
        "4. Intentar registrar cliente con teléfono inválido",
        lambda: sistema_pruebas.registrar_cliente(
            "Pedro Díaz", "pedro@gmail.com", "12345"
        )
    )

    # 5. Registrar sala
    ejecutar_operacion(
        "5. Registrar servicio de sala",
        lambda: sistema_pruebas.registrar_servicio(
            ReservaSala("Sala principal", 50000, 15)
        ).obtener_resumen()
    )

    # 6. Registrar equipos
    ejecutar_operacion(
        "6. Registrar servicio de alquiler de equipos",
        lambda: sistema_pruebas.registrar_servicio(
            AlquilerEquipo("Proyector", 40000, 5)
        ).obtener_resumen()
    )

    # 7. Registrar asesoría
    ejecutar_operacion(
        "7. Registrar asesoría especializada",
        lambda: sistema_pruebas.registrar_servicio(
            AsesoriaEspecializada("Asesoría tecnológica", 70000, "virtual")
        ).obtener_resumen()
    )

    cliente = sistema_pruebas.clientes[0]
    sala = sistema_pruebas.servicios[0]

    # 8. Crear, confirmar y procesar una reserva válida
    def reserva_valida():
        reserva = sistema_pruebas.crear_reserva(
            cliente.identificador, sala.identificador, 2,
            {"horas": 2, "asistentes": 10, "impuesto": 0.19}
        )
        reserva.confirmar()
        total = reserva.procesar()
        return f"{reserva.obtener_resumen()} | Costo calculado: ${total:,.2f}"

    ejecutar_operacion("8. Crear y procesar reserva válida", reserva_valida)

    # 9. Intentar reservar una sala con demasiados asistentes
    def reserva_exceso_asistentes():
        reserva = sistema_pruebas.crear_reserva(
            cliente.identificador, sala.identificador, 2,
            {"horas": 2, "asistentes": 30}
        )
        reserva.confirmar()
        return reserva.procesar()

    ejecutar_operacion("9. Intentar reserva con exceso de asistentes", reserva_exceso_asistentes)

    # 10. Buscar cliente inexistente
    ejecutar_operacion(
        "10. Buscar cliente inexistente",
        lambda: sistema_pruebas.buscar_cliente(9999)
    )

    # 11. Intentar cancelar una reserva procesada
    def cancelar_procesada():
        reserva = sistema_pruebas.reservas[0]
        reserva.cancelar()
        return reserva.obtener_resumen()

    ejecutar_operacion("11. Intentar cancelar reserva procesada", cancelar_procesada)

    # 12. Cálculo con descuento
    def costo_con_descuento():
        equipo = sistema_pruebas.servicios[1]
        total = equipo.calcular_costo(cantidad=2, dias=3, descuento=0.10)
        return f"Costo del alquiler con descuento: ${total:,.2f}"

    ejecutar_operacion("12. Calcular alquiler con descuento", costo_con_descuento)

    print("\n========== FIN DE LAS PRUEBAS ==========")
    print("El sistema continuó funcionando después de los errores.")


# ==========================================================
# FUNCIONES DEL MENÚ INTERACTIVO
# ==========================================================

def mostrar_clientes():
    print("\n========== CLIENTES REGISTRADOS ==========")
    if not sistema.clientes:
        print("No hay clientes registrados.")
    else:
        for cliente in sistema.clientes:
            print(cliente.obtener_resumen())


def mostrar_servicios():
    print("\n========== SERVICIOS DISPONIBLES ==========")
    if not sistema.servicios:
        print("No hay servicios registrados.")
    else:
        for servicio in sistema.servicios:
            print(servicio.obtener_resumen())
            print("Descripción:", servicio.describir_servicio())


def mostrar_reservas():
    print("\n========== RESERVAS ==========")
    if not sistema.reservas:
        print("No hay reservas registradas.")
    else:
        for reserva in sistema.reservas:
            print(reserva.obtener_resumen())


def menu_principal():
    cargar_servicios_iniciales()

    while True:
        print("\n================================================")
        print("       SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
        print("================================================")
        print("1. Registrar cliente")
        print("2. Consultar clientes")
        print("3. Consultar servicios")
        print("4. Crear reserva")
        print("5. Consultar reservas")
        print("6. Ejecutar simulación de 12 operaciones")
        print("7. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            try:
                nombre = input("Nombre y apellido: ")
                correo = input("Correo electrónico: ")
                telefono = input("Teléfono de 10 dígitos: ")
                cliente = sistema.registrar_cliente(nombre, correo, telefono)
                print("Cliente registrado:", cliente.obtener_resumen())
            except ErrorSistema as error:
                print("No se pudo registrar el cliente:", error)
                logging.error("Registro de cliente fallido: %s", error)

        elif opcion == "2":
            mostrar_clientes()

        elif opcion == "3":
            mostrar_servicios()

        elif opcion == "4":
            try:
                mostrar_clientes()
                id_cliente = int(input("Ingrese el identificador del cliente: "))
                mostrar_servicios()
                id_servicio = int(input("Ingrese el identificador del servicio: "))
                servicio = sistema.buscar_servicio(id_servicio)

                if isinstance(servicio, ReservaSala):
                    horas = float(input("Número de horas: "))
                    asistentes = int(input("Número de asistentes: "))
                    parametros = {"horas": horas, "asistentes": asistentes}

                elif isinstance(servicio, AlquilerEquipo):
                    cantidad = int(input("Cantidad de equipos: "))
                    dias = int(input("Número de días: "))
                    parametros = {"cantidad": cantidad, "dias": dias}

                elif isinstance(servicio, AsesoriaEspecializada):
                    horas = float(input("Número de horas de asesoría: "))
                    modalidad = input("Modalidad (virtual/presencial): ").strip().lower()
                    parametros = {"horas": horas, "modalidad": modalidad}

                else:
                    parametros = {}

                reserva = sistema.crear_reserva(
                    id_cliente, id_servicio, 1, parametros
                )
                reserva.confirmar()
                total = reserva.procesar()
                print("Reserva realizada correctamente.")
                print(reserva.obtener_resumen())
                print(f"Total a pagar: ${total:,.2f}")

            except ValueError:
                print("Error: debe ingresar números válidos.")
                logging.error("Se ingresó un valor numérico inválido al crear reserva.")
            except ErrorSistema as error:
                print("No fue posible crear la reserva:", error)
                logging.error("Error al crear reserva: %s", error)
            finally:
                print("Proceso de reserva finalizado.")

        elif opcion == "5":
            mostrar_reservas()

        elif opcion == "6":
            ejecutar_pruebas()

        elif opcion == "7":
            print("\nGracias por utilizar Software FJ.")
            print("Sistema finalizado correctamente.")
            break

        else:
            print("Opción no válida. Intente nuevamente.")


# ==========================================================
# INICIO DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":
    menu_principal()
