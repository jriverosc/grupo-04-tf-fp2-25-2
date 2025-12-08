import datetime
import os
from abc import ABC, abstractmethod

# Patrón Observer para las alertas de stock mínimo
class Observador(ABC):
    @abstractmethod
    def actualizar(self, producto):
        pass

class AlertaStockMinimo(Observador):
    def actualizar(self, producto):
        # Esta función se mantiene para el patrón Observer pero no se usa para mostrar mensajes
        pass

# Clase Producto
class Producto:
    def __init__(self, codigo, nombre, categoria, stock_minimo, proveedor, costo_unitario=0):
        self.__codigo = codigo
        self.__nombre = nombre
        self.__categoria = categoria
        self.__stock_minimo = stock_minimo
        self.__proveedor = proveedor
        self.__costo_unitario = costo_unitario
        self.__stock_actual = 0
        self.__observadores = []

    # Getters
    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def categoria(self):
        return self.__categoria

    @property
    def stock_minimo(self):
        return self.__stock_minimo

    @property
    def proveedor(self):
        return self.__proveedor

    @property
    def costo_unitario(self):
        return self.__costo_unitario

    @property
    def stock_actual(self):
        return self.__stock_actual

    def agregar_observador(self, observador):
        self.__observadores.append(observador)

    def notificar_observadores(self):
        for observador in self.__observadores:
            observador.actualizar(self)

    def actualizar_stock(self, cantidad):
        self.__stock_actual += cantidad
        self.notificar_observadores()

    def verificar_stock_minimo(self):
        return self.__stock_actual <= self.__stock_minimo

    def __str__(self):
        estado = "BAJO" if self.verificar_stock_minimo() else "OK"
        return f"{self.__codigo} - {self.__nombre} | Categoria: {self.__categoria} | Stock: {self.__stock_actual} | Minimo: {self.__stock_minimo} | Estado: {estado}"

# Clase Movimiento (Patrón Factory)
class Movimiento:
    def __init__(self, tipo, producto, cantidad, fecha=None, usuario="Sistema"):
        self.__tipo = tipo  # 'ingreso' o 'salida'
        self.__producto = producto
        self.__cantidad = cantidad
        self.__fecha = fecha if fecha else datetime.datetime.now()
        self.__usuario = usuario

    # Getters
    @property
    def tipo(self):
        return self.__tipo

    @property
    def producto(self):
        return self.__producto

    @property
    def cantidad(self):
        return self.__cantidad

    @property
    def fecha(self):
        return self.__fecha

    @property
    def usuario(self):
        return self.__usuario

    @staticmethod
    def crear_movimiento(tipo, producto, cantidad, usuario="Sistema"):
        return Movimiento(tipo, producto, cantidad, usuario=usuario)

    def __str__(self):
        return f"{self.__fecha.strftime('%Y-%m-%d %H:%M')} | {self.__tipo.upper()} | {self.__producto.nombre} | Cantidad: {self.__cantidad} | Usuario: {self.__usuario}"

# Sistema de Inventario (Singleton)
class SistemaInventario:
    __instancia = None

    def __new__(cls):
        if cls.__instancia is None:
            cls.__instancia = super().__new__(cls)
            cls.__instancia.__productos = {}
            cls.__instancia.__movimientos = []
            cls.__instancia.__alertas = AlertaStockMinimo()
        return cls.__instancia

    def registrar_producto(self, codigo, nombre, categoria, stock_minimo, proveedor, costo_unitario=0):
        if codigo in self.__productos:
            print("Error: El codigo del producto ya existe")
            return None
        
        producto = Producto(codigo, nombre, categoria, stock_minimo, proveedor, costo_unitario)
        producto.agregar_observador(self.__alertas)
        self.__productos[codigo] = producto
        return producto

    def buscar_producto(self, criterio, valor):
        resultados = []
        for producto in self.__productos.values():
            if (criterio == "codigo" and valor.lower() in producto.codigo.lower()) or \
               (criterio == "nombre" and valor.lower() in producto.nombre.lower()) or \
               (criterio == "categoria" and valor.lower() in producto.categoria.lower()):
                resultados.append(producto)
        return resultados

    def registrar_ingreso(self, codigo_producto, cantidad, tipo_ingreso="compra", usuario="Sistema"):
        if codigo_producto not in self.__productos:
            print("Error: Producto no encontrado")
            return None
        
        producto = self.__productos[codigo_producto]
        movimiento = Movimiento.crear_movimiento(f"ingreso_{tipo_ingreso}", producto, cantidad, usuario)
        self.__movimientos.append(movimiento)
        producto.actualizar_stock(cantidad)
        return movimiento

    def registrar_salida(self, codigo_producto, cantidad, tipo_salida="venta", usuario="Sistema"):
        if codigo_producto not in self.__productos:
            print("Error: Producto no encontrado")
            return None
        
        producto = self.__productos[codigo_producto]
        if producto.stock_actual < cantidad:
            print("Error: Stock insuficiente para realizar la salida")
            return None
        
        movimiento = Movimiento.crear_movimiento(f"salida_{tipo_salida}", producto, -cantidad, usuario)
        self.__movimientos.append(movimiento)
        producto.actualizar_stock(-cantidad)
        return movimiento

    def generar_reporte_stock(self):
        print("\n" + "="*80)
        print("REPORTE DE STOCK ACTUAL")
        print("="*80)
        print(f"{'Codigo':<10} {'Nombre':<20} {'Categoria':<15} {'Stock':<8} {'Minimo':<8} {'Estado':<10}")
        print("-"*80)
        
        productos_bajo_stock = []
        
        for producto in self.__productos.values():
            estado = "BAJO" if producto.verificar_stock_minimo() else "OK"
            print(f"{producto.codigo:<10} {producto.nombre:<20} {producto.categoria:<15} {producto.stock_actual:<8} {producto.stock_minimo:<8} {estado:<10}")
            
            if producto.verificar_stock_minimo():
                productos_bajo_stock.append(producto)
        
        # Mostrar alertas de stock mínimo al final
        if productos_bajo_stock:
            print("\n--- ALERTAS DE STOCK MINIMO ---")
            for producto in productos_bajo_stock:
                print(f"El producto {producto.nombre} esta por debajo del stock minimo, Stock = {producto.stock_actual}")

    def mostrar_productos_ordenados(self):
        print("\n" + "="*80)
        print("LISTA COMPLETA DE PRODUCTOS")
        print("="*80)
        print(f"{'Codigo':<10} {'Nombre':<20} {'Categoria':<15} {'Stock':<8} {'Minimo':<8} {'Estado':<10}")
        print("-"*80)
        
        productos_bajo_stock = []
        
        # Ordenar productos por nombre
        productos_ordenados = sorted(self.__productos.values(), key=lambda x: x.nombre)
        
        for producto in productos_ordenados:
            estado = "BAJO" if producto.verificar_stock_minimo() else "OK"
            print(f"{producto.codigo:<10} {producto.nombre:<20} {producto.categoria:<15} {producto.stock_actual:<8} {producto.stock_minimo:<8} {estado:<10}")
            
            if producto.verificar_stock_minimo():
                productos_bajo_stock.append(producto)
        
        # Mostrar alertas de stock mínimo al final
        if productos_bajo_stock:
            print("\n--- ALERTAS DE STOCK MINIMO ---")
            for producto in productos_bajo_stock:
                print(f"El producto {producto.nombre} esta por debajo del stock minimo, Stock = {producto.stock_actual}")

    def calcular_valor_inventario(self):
        valor_total = 0
        print("\n" + "="*60)
        print("VALOR DEL INVENTARIO")
        print("="*60)
        print(f"{'Producto':<20} {'Stock':<8} {'Costo Unit.':<12} {'Valor Total':<12}")
        print("-"*60)
        
        for producto in self.__productos.values():
            valor_producto = producto.stock_actual * producto.costo_unitario
            valor_total += valor_producto
            print(f"{producto.nombre:<20} {producto.stock_actual:<8} ${producto.costo_unitario:<11.2f} ${valor_producto:<11.2f}")
        
        print("-"*60)
        print(f"{'VALOR TOTAL DEL INVENTARIO:':<40} ${valor_total:.2f}")

    def obtener_historial_movimientos(self, codigo_producto=None, fecha_inicio=None, fecha_fin=None):
        movimientos_filtrados = self.__movimientos
        
        if codigo_producto:
            movimientos_filtrados = [m for m in movimientos_filtrados if m.producto.codigo == codigo_producto]
        
        if fecha_inicio:
            movimientos_filtrados = [m for m in movimientos_filtrados if m.fecha >= fecha_inicio]
        
        if fecha_fin:
            movimientos_filtrados = [m for m in movimientos_filtrados if m.fecha <= fecha_fin]
        
        return movimientos_filtrados

    def mostrar_historial(self, codigo_producto=None):
        historial = self.obtener_historial_movimientos(codigo_producto)
        
        if codigo_producto:
            producto = self.__productos.get(codigo_producto)
            titulo = f"HISTORIAL DE MOVIMIENTOS - {producto.nombre if producto else codigo_producto}"
        else:
            titulo = "HISTORIAL COMPLETO DE MOVIMIENTOS"
        
        print(f"\n{titulo}")
        print("="*80)
        if not historial:
            print("No hay movimientos registrados")
            return
        
        for movimiento in historial:
            print(movimiento)

    def mostrar_producto_especifico(self, producto):
        print("\n--- INFORMACION DEL PRODUCTO ---")
        print(f"Codigo: {producto.codigo}")
        print(f"Nombre: {producto.nombre}")
        print(f"Categoria: {producto.categoria}")
        print(f"Proveedor: {producto.proveedor}")
        print(f"Stock actual: {producto.stock_actual}")
        print(f"Stock minimo: {producto.stock_minimo}")
        print(f"Costo unitario: ${producto.costo_unitario:.2f}")
        
        if producto.verificar_stock_minimo():
            print(f"\nALERTA: El producto {producto.nombre} esta por debajo del stock minimo, Stock = {producto.stock_actual}")

# Menú principal
class MenuSistema:
    def __init__(self):
        self.__sistema = SistemaInventario()

    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def mostrar_menu(self):
        while True:
            self.limpiar_pantalla()
            print("="*50)
            print("     SISTEMA DE INVENTARIO - METAL-MECANICA SAC")
            print("="*50)
            print("1. Registrar producto")
            print("2. Buscar producto")
            print("3. Registrar ingreso de productos")
            print("4. Registrar salida de productos")
            print("5. Generar reporte de stock")
            print("6. Mostrar lista completa de productos")
            print("7. Calcular valor del inventario")
            print("8. Mostrar historial de movimientos")
            print("9. Salir")
            print("-"*50)

            opcion = input("Seleccione una opcion: ")

            if opcion == "1":
                self.registrar_producto()
            elif opcion == "2":
                self.buscar_producto()
            elif opcion == "3":
                self.registrar_ingreso()
            elif opcion == "4":
                self.registrar_salida()
            elif opcion == "5":
                self.generar_reporte_stock()
            elif opcion == "6":
                self.mostrar_lista_completa()
            elif opcion == "7":
                self.calcular_valor_inventario()
            elif opcion == "8":
                self.mostrar_historial()
            elif opcion == "9":
                print("Gracias por usar el sistema!")
                break
            else:
                print("Opcion invalida. Por favor, seleccione 1-9")
            
            input("\nPresione Enter para continuar...")

    def registrar_producto(self):
        print("\n--- REGISTRAR NUEVO PRODUCTO ---")
        codigo = input("Codigo del producto: ")
        nombre = input("Nombre: ")
        categoria = input("Categoria: ")
        stock_minimo = int(input("Stock minimo: "))
        proveedor = input("Proveedor: ")
        costo_unitario = float(input("Costo unitario: "))
        
        producto = self.__sistema.registrar_producto(codigo, nombre, categoria, stock_minimo, proveedor, costo_unitario)
        if producto:
            print(f"Producto '{producto.nombre}' registrado exitosamente")

    def buscar_producto(self):
        print("\n--- BUSCAR PRODUCTO ---")
        print("1. Por codigo")
        print("2. Por nombre")
        print("3. Por categoria")
        opcion = input("Seleccione criterio de busqueda: ")

        criterios = {"1": "codigo", "2": "nombre", "3": "categoria"}
        criterio = criterios.get(opcion)
        
        if not criterio:
            print("Opcion invalida")
            return

        valor = input("Ingrese el valor a buscar: ")
        resultados = self.__sistema.buscar_producto(criterio, valor)
        
        if resultados:
            print(f"\nProductos encontrados ({len(resultados)}):")
            for producto in resultados:
                self.__sistema.mostrar_producto_especifico(producto)
                print("-" * 40)
        else:
            print("No se encontraron productos")

    def registrar_ingreso(self):
        print("\n--- REGISTRAR INGRESO DE PRODUCTOS ---")
        codigo = input("Codigo del producto: ")
        cantidad = int(input("Cantidad: "))
        tipo = input("Tipo de ingreso (compra/devolucion/ajuste/traslado): ").lower()
        usuario = input("Usuario que registra: ") or "Sistema"
        
        movimiento = self.__sistema.registrar_ingreso(codigo, cantidad, tipo, usuario)
        if movimiento:
            print(f"Ingreso registrado: {movimiento}")

    def registrar_salida(self):
        print("\n--- REGISTRAR SALIDA DE PRODUCTOS ---")
        codigo = input("Codigo del producto: ")
        cantidad = int(input("Cantidad: "))
        tipo = input("Tipo de salida (venta/ajuste/traslado): ").lower()
        usuario = input("Usuario que registra: ") or "Sistema"
        
        movimiento = self.__sistema.registrar_salida(codigo, cantidad, tipo, usuario)
        if movimiento:
            print(f"Salida registrada: {movimiento}")

    def generar_reporte_stock(self):
        self.__sistema.generar_reporte_stock()

    def mostrar_lista_completa(self):
        self.__sistema.mostrar_productos_ordenados()

    def calcular_valor_inventario(self):
        self.__sistema.calcular_valor_inventario()

    def mostrar_historial(self):
        print("\n--- HISTORIAL DE MOVIMIENTOS ---")
        print("1. Historial completo")
        print("2. Historial por producto")
        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            self.__sistema.mostrar_historial()
        elif opcion == "2":
            codigo = input("Ingrese el codigo del producto: ")
            self.__sistema.mostrar_historial(codigo)
        else:
            print("Opcion invalida")

# Función principal
def main():
    # Crear algunos datos de ejemplo
    sistema = SistemaInventario()
    
    # Productos de ejemplo
    productos_ejemplo = [
        ("AC001", "Tornillo Acero 5mm", "Tornilleria", 100, "Aceros SAC", 0.50),
        ("PL002", "Placa Aluminio 2x1m", "Planchas", 10, "Aluminios Peru", 25.00),
        ("HR003", "Herramienta Cortadora", "Herramientas", 5, "Herramental SA", 15.75)
    ]
    
    for prod in productos_ejemplo:
        try:
            sistema.registrar_producto(*prod)
            # Registrar algunos movimientos de ejemplo
            sistema.registrar_ingreso(prod[0], prod[3] * 2, "compra")
        except:
            pass
    
    # Iniciar el menú
    menu = MenuSistema()
    menu.mostrar_menu()

if __name__ == "__main__":
    main()