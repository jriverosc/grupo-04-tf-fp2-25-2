import datetime
from abc import ABC, abstractmethod


#   EXCEPCIONES PERSONALIZADAS

class ErrorInventario(Exception):
    """Excepción base para errores del inventario"""
    pass

class ProductoNoEncontrado(ErrorInventario):
    """Se lanza cuando no se encuentra un producto"""
    pass

class StockInsuficiente(ErrorInventario):
    """Se lanza cuando no hay suficiente stock"""
    pass

class CodigoDuplicado(ErrorInventario):
    """Se lanza cuando se intenta registrar un código existente"""
    pass


#   CLASE PROVEEDOR (COMPOSICIÓN)

class Proveedor:
    """Clase para representar proveedores (COMPOSICIÓN en Producto)"""
    def __init__(self, nombre, ruc="00000000000", telefono="999999999"):
        self.__nombre = nombre
        self.__ruc = ruc
        self.__telefono = telefono

    # Getters
    @property
    def nombre(self):
        return self.__nombre

    @property
    def ruc(self):
        return self.__ruc

    @property
    def telefono(self):
        return self.__telefono

    def __str__(self):
        return f"{self.__nombre} (RUC: {self.__ruc}, Tel: {self.__telefono})"


#   CLASE PRODUCTO BASE (Abstracta)

class Producto(ABC):
    def __init__(self, codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario=0):
        self.__codigo = codigo
        self.__nombre = nombre
        self.__categoria = categoria
        self.__stock_minimo = stock_minimo
        
        # COMPOSICIÓN : Producto contiene un objeto Proveedor
        if isinstance(proveedor_info, Proveedor):
            self.__proveedor = proveedor_info
        else:
            self.__proveedor = Proveedor(proveedor_info)
        
        self.__costo_unitario = costo_unitario
        self.__stock_actual = 0
        self.__movimientos = []  # MULTIPLICIDAD

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

    def actualizar_stock(self, cantidad):
        """Actualiza el stock del producto"""
        self.__stock_actual += cantidad

    def verificar_stock_minimo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.__stock_actual <= self.__stock_minimo

    def agregar_movimiento(self, movimiento):
        self.__movimientos.append(movimiento)

    def obtener_movimientos(self):
        return list(self.__movimientos)

    def mostrar_alerta_stock(self):
        """Muestra alerta de stock mínimo SOLO cuando se llama"""
        if self.verificar_stock_minimo():
            print(f"\n--- ALERTA DE STOCK MINIMO ---")
            print(f"El producto '{self.nombre}' está por debajo del stock mínimo.")
            print(f"Stock actual: {self.stock_actual}")
            print(f"Stock mínimo requerido: {self.stock_minimo}")
            print(f"Faltan: {self.stock_minimo - self.stock_actual} unidades")
            print("---" + "-" * 30)

    def __str__(self):
        estado = "BAJO" if self.verificar_stock_minimo() else "OK"
        return f"{self.__codigo} - {self.__nombre} | Categoria: {self.__categoria} | Stock: {self.__stock_actual} | Minimo: {self.__stock_minimo} | Estado: {estado}"


#   SUBCLASES DE PRODUCTO (NACIONAL E IMPORTADO)


# Producto Nacional: tiene origen nacional
class ProductoNacional(Producto):
    def __init__(self, codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario, region_origen):
        super().__init__(codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario)
        self.__region_origen = region_origen

    @property
    def region_origen(self):
        return self.__region_origen

    def __str__(self):
        base = super().__str__()
        return f"{base} | Origen: {self.__region_origen}"

# Producto Importado: tiene un impuesto adicional
class ProductoImportado(Producto):
    def __init__(self, codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario, impuesto):
        super().__init__(codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario)
        self.__impuesto = impuesto

    def costo_con_impuesto(self):
        return self.costo_unitario * (1 + self.__impuesto)

    @property
    def impuesto(self):
        return self.__impuesto

    def __str__(self):
        base = super().__str__()
        return f"{base} | Impuesto: {self.__impuesto*100:.0f}% | Costo final: ${self.costo_con_impuesto():.2f}"


#   CLASE MOVIMIENTO (con AGREGACIÓN de Producto)

class Movimiento:
    def __init__(self, tipo, producto, cantidad, fecha=None, usuario="Sistema"):
        self.__tipo = tipo
        
        if not isinstance(producto, Producto):
            raise TypeError("Movimiento debe recibir un objeto Producto válido")
        
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
        return Movimiento(tipo, producto, cantidad, None, usuario)

    def __str__(self):
        return f"{self.__fecha.strftime('%Y-%m-%d %H:%M')} | {self.__tipo.upper()} | {self.__producto.nombre} | Cantidad: {self.__cantidad} | Usuario: {self.__usuario}"


#   SISTEMA DE INVENTARIO

class SistemaInventario:
    __instancia = None

    def __new__(cls):
        if cls.__instancia is None:
            cls.__instancia = super().__new__(cls)
            cls.__instancia.__productos = {}
            cls.__instancia.__movimientos = []
        return cls.__instancia

    def registrar_producto(self, codigo, nombre, categoria, stock_minimo, proveedor_info, costo_unitario=0, tipo_producto="nacional", datos_extra=None):
        """
        tipo_producto: "nacional" o "importado"
        datos_extra: dict con datos específicos según tipo
          - nacional: {"region_origen": "Lima"}
          - importado: {"impuesto": 0.18}
        """
        if codigo in self.__productos:
            raise CodigoDuplicado(f"Error: El codigo '{codigo}' ya existe en el sistema")

        if tipo_producto == "nacional":
            if not datos_extra or "region_origen" not in datos_extra:
                raise ValueError("Producto nacional requiere 'region_origen' en datos_extra")
            producto = ProductoNacional(codigo, nombre, categoria, stock_minimo, proveedor_info, 
                                       costo_unitario, datos_extra["region_origen"])
        
        elif tipo_producto == "importado":
            if not datos_extra or "impuesto" not in datos_extra:
                raise ValueError("Producto importado requiere 'impuesto' en datos_extra")
            producto = ProductoImportado(codigo, nombre, categoria, stock_minimo, proveedor_info, 
                                        costo_unitario, datos_extra["impuesto"])
        
        else:
            raise ValueError(f"Tipo de producto no válido: {tipo_producto}. Use 'nacional' o 'importado'")

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
            raise ProductoNoEncontrado(f"Error: Producto con codigo '{codigo_producto}' no encontrado")

        producto = self.__productos[codigo_producto]
        movimiento = Movimiento.crear_movimiento(f"ingreso_{tipo_ingreso}", producto, cantidad, usuario)
        self.__movimientos.append(movimiento)
        producto.actualizar_stock(cantidad)
        producto.agregar_movimiento(movimiento)
        return movimiento

    def registrar_salida(self, codigo_producto, cantidad, tipo_salida="venta", usuario="Sistema"):
        if codigo_producto not in self.__productos:
            raise ProductoNoEncontrado(f"Error: Producto con codigo '{codigo_producto}' no encontrado")

        producto = self.__productos[codigo_producto]
        if producto.stock_actual < cantidad:
            raise StockInsuficiente(
                f"Error: Stock insuficiente para '{producto.nombre}'. "
                f"Stock actual: {producto.stock_actual}, Solicitado: {cantidad}"
            )

        movimiento = Movimiento.crear_movimiento(f"salida_{tipo_salida}", producto, -cantidad, usuario)
        self.__movimientos.append(movimiento)
        producto.actualizar_stock(-cantidad)
        producto.agregar_movimiento(movimiento)
        return movimiento

    def generar_reporte_stock(self):
        print("\n" + "="*80)
        print("REPORTE DE STOCK ACTUAL")
        print("="*80)
        print(f"{'Codigo':<10} {'Nombre':<30} {'Categoria':<15} {'Stock':<8} {'Minimo':<8} {'Estado':<10} {'Tipo':<12}")
        print("-"*80)

        productos_bajo_stock = []

        for producto in self.__productos.values():
            estado = "BAJO" if producto.verificar_stock_minimo() else "OK"
            tipo = "NACIONAL" if isinstance(producto, ProductoNacional) else "IMPORTADO"
            print(f"{producto.codigo:<10} {producto.nombre:<30} {producto.categoria:<15} "
                  f"{producto.stock_actual:<8} {producto.stock_minimo:<8} {estado:<10} {tipo:<12}")

            if producto.verificar_stock_minimo():
                productos_bajo_stock.append(producto)

        # SOLO se muestran alertas si hay productos con bajo stock
        if productos_bajo_stock:
            print("\n--- PRODUCTOS CON STOCK BAJO MINIMO ---")
            for producto in productos_bajo_stock:
                print(f"• {producto.nombre}: Stock actual {producto.stock_actual} (Mínimo: {producto.stock_minimo})")

    def mostrar_productos_ordenados(self):
        print("\n" + "="*80)
        print("LISTA COMPLETA DE PRODUCTOS")
        print("="*80)
        print(f"{'Codigo':<10} {'Nombre':<30} {'Categoria':<15} {'Stock':<8} {'Minimo':<8} {'Estado':<10} {'Tipo':<12}")
        print("-"*80)

        productos_bajo_stock = []

        productos_ordenados = sorted(self.__productos.values(), key=lambda x: x.nombre)

        for producto in productos_ordenados:
            estado = "BAJO" if producto.verificar_stock_minimo() else "OK"
            tipo = "NACIONAL" if isinstance(producto, ProductoNacional) else "IMPORTADO"
            print(f"{producto.codigo:<10} {producto.nombre:<30} {producto.categoria:<15} "
                  f"{producto.stock_actual:<8} {producto.stock_minimo:<8} {estado:<10} {tipo:<12}")

            if producto.verificar_stock_minimo():
                productos_bajo_stock.append(producto)

        # SOLO se muestran alertas si hay productos con bajo stock
        if productos_bajo_stock:
            print("\n--- PRODUCTOS CON STOCK BAJO MINIMO ---")
            for producto in productos_bajo_stock:
                print(f"• {producto.nombre}: Stock actual {producto.stock_actual} (Mínimo: {producto.stock_minimo})")

    def calcular_valor_inventario(self):
        valor_total = 0
        print("\n" + "="*60)
        print("VALOR DEL INVENTARIO")
        print("="*60)
        print(f"{'Producto':<30} {'Tipo':<12} {'Stock':<8} {'Costo Unit.':<12} {'Valor Total':<12}")
        print("-"*60)

        for producto in self.__productos.values():
            costo_unit = producto.costo_unitario
            tipo = "NACIONAL" if isinstance(producto, ProductoNacional) else "IMPORTADO"
            
            if hasattr(producto, "costo_con_impuesto"):
                costo_unit = producto.costo_con_impuesto()
            
            valor_producto = producto.stock_actual * costo_unit
            valor_total += valor_producto
            print(f"{producto.nombre:<30} {tipo:<12} {producto.stock_actual:<8} ${costo_unit:<11.2f} ${valor_producto:<11.2f}")

        print("-"*60)
        print(f"{'VALOR TOTAL DEL INVENTARIO:':<52} ${valor_total:.2f}")

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
        """Muestra información detallada de un producto y SU ALERTA SI ES NECESARIO"""
        print("\n--- INFORMACION DEL PRODUCTO ---")
        print(f"Codigo: {producto.codigo}")
        print(f"Nombre: {producto.nombre}")
        print(f"Categoria: {producto.categoria}")
        print(f"Proveedor: {producto.proveedor}")
        print(f"Stock actual: {producto.stock_actual}")
        print(f"Stock minimo: {producto.stock_minimo}")
        
        if isinstance(producto, ProductoNacional):
            print(f"Tipo: NACIONAL")
            print(f"Region de origen: {producto.region_origen}")
            print(f"Costo unitario: ${producto.costo_unitario:.2f}")
        elif isinstance(producto, ProductoImportado):
            print(f"Tipo: IMPORTADO")
            print(f"Impuesto de importacion: {producto.impuesto*100:.0f}%")
            print(f"Costo con impuesto: ${producto.costo_con_impuesto():.2f}")

        # SE MUESTRA LA ALERTA SOLO CUANDO SE BUSCA EL PRODUCTO
        producto.mostrar_alerta_stock()

        movimientos = producto.obtener_movimientos()
        if movimientos:
            print("\nMovimientos del producto:")
            for m in movimientos:
                print(f"  - {m}")


#   MENÚ PRINCIPAL

class MenuSistema:
    def __init__(self):
        self.__sistema = SistemaInventario()

    def limpiar_pantalla(self):
        print("\n" * 50)

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

            try:
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
                    
            except Exception as e:
                print(f"\nError inesperado: {e}")
            
            input("\nPresione Enter para continuar...")

    def registrar_producto(self):
        self.limpiar_pantalla()
        print("\n--- REGISTRAR NUEVO PRODUCTO ---")
        
        try:
            codigo = input("Codigo del producto: ")
            nombre = input("Nombre: ")
            categoria = input("Categoria: ")
            stock_minimo = int(input("Stock minimo: "))
            proveedor_nombre = input("Nombre del proveedor: ")
            proveedor_ruc = input("RUC del proveedor (opcional): ") or "00000000000"
            proveedor_tel = input("Telefono del proveedor (opcional): ") or "999999999"
            costo_unitario = float(input("Costo unitario: "))

            print("\nTipo de producto:")
            print("1. Nacional")
            print("2. Importado")
            tipo_opcion = input("Seleccione tipo (1-2): ")

            tipo_producto = ""
            datos_extra = {}
            
            if tipo_opcion == "1":
                tipo_producto = "nacional"
                region = input("Region de origen (ej: Lima, Arequipa, Cusco): ")
                datos_extra = {"region_origen": region}
                
            elif tipo_opcion == "2":
                tipo_producto = "importado"
                impuesto = float(input("Impuesto (ej: 0.18 para 18%): "))
                datos_extra = {"impuesto": impuesto}
                
            else:
                print("Opcion invalida. Debe seleccionar 1 o 2")
                return

            proveedor = Proveedor(proveedor_nombre, proveedor_ruc, proveedor_tel)
            
            producto = self.__sistema.registrar_producto(
                codigo, nombre, categoria, stock_minimo, 
                proveedor, costo_unitario, tipo_producto, datos_extra
            )
            
            if producto:
                print(f"\nProducto '{producto.nombre}' registrado exitosamente")
                print(f"Tipo: {tipo_producto.upper()}")
                print(f"Proveedor: {proveedor}")

        except CodigoDuplicado as e:
            print(f"\n{e}")
        except ValueError as e:
            print(f"\nError en los datos ingresados: {e}")
        except Exception as e:
            print(f"\nError inesperado: {e}")

    def buscar_producto(self):
        self.limpiar_pantalla()
        print("\n--- BUSCAR PRODUCTO ---")
        
        try:
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
                
        except Exception as e:
            print(f"Error: {e}")

    def registrar_ingreso(self):
        self.limpiar_pantalla()
        print("\n--- REGISTRAR INGRESO DE PRODUCTOS ---")
        
        try:
            codigo = input("Codigo del producto: ")
            cantidad = int(input("Cantidad: "))
            tipo = input("Tipo de ingreso (compra/devolucion/ajuste/traslado): ").lower()
            usuario = input("Usuario que registra: ") or "Sistema"

            movimiento = self.__sistema.registrar_ingreso(codigo, cantidad, tipo, usuario)
            print(f"\nIngreso registrado: {movimiento}")
            
        except ProductoNoEncontrado as e:
            print(f"\n{e}")
        except ValueError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nError inesperado: {e}")

    def registrar_salida(self):
        self.limpiar_pantalla()
        print("\n--- REGISTRAR SALIDA DE PRODUCTOS ---")
        
        try:
            codigo = input("Codigo del producto: ")
            cantidad = int(input("Cantidad: "))
            tipo = input("Tipo de salida (venta/ajuste/traslado): ").lower()
            usuario = input("Usuario que registra: ") or "Sistema"

            movimiento = self.__sistema.registrar_salida(codigo, cantidad, tipo, usuario)
            print(f"\nSalida registrada: {movimiento}")
            
        except ProductoNoEncontrado as e:
            print(f"\n{e}")
        except StockInsuficiente as e:
            print(f"\n{e}")
        except ValueError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nError inesperado: {e}")

    def generar_reporte_stock(self):
        self.limpiar_pantalla()
        self.__sistema.generar_reporte_stock()

    def mostrar_lista_completa(self):
        self.limpiar_pantalla()
        self.__sistema.mostrar_productos_ordenados()

    def calcular_valor_inventario(self):
        self.limpiar_pantalla()
        self.__sistema.calcular_valor_inventario()

    def mostrar_historial(self):
        self.limpiar_pantalla()
        print("\n--- HISTORIAL DE MOVIMIENTOS ---")
        print("1. Historial completo")
        print("2. Historial por producto")
        
        try:
            opcion = input("Seleccione una opcion: ")

            if opcion == "1":
                self.__sistema.mostrar_historial()
            elif opcion == "2":
                codigo = input("Ingrese el codigo del producto: ")
                self.__sistema.mostrar_historial(codigo)
            else:
                print("Opcion invalida")
                
        except Exception as e:
            print(f"Error: {e}")


#   FUNCIÓN PRINCIPAL

def main():
    sistema = SistemaInventario()

    try:
        proveedor_aceros = Proveedor("Aceros SAC", "20123456789", "987654321")
        proveedor_aluminios = Proveedor("Aluminios Peru", "20123456788", "987654322")
        proveedor_aceros_peru = Proveedor("Aceros Peru", "20123456787", "987654323")
        proveedor_bosch = Proveedor("Bosch Import", "20123456786", "987654324")

        sistema.registrar_producto("NA001", "Varilla de Acero Nacional", "Materiales", 
                                  50, proveedor_aceros_peru, 15.00, "nacional", 
                                  {"region_origen": "Lima"})
        
        sistema.registrar_producto("IM001", "Taladro Bosch", "Herramientas", 
                                  3, proveedor_bosch, 120.00, "importado", 
                                  {"impuesto": 0.18})
        
        sistema.registrar_producto("NA002", "Tornillo Acero 5mm", "Tornilleria", 
                                  100, proveedor_aceros, 0.50, "nacional",
                                  {"region_origen": "Arequipa"})
        
        sistema.registrar_producto("IM002", "Placa Aluminio 2x1m", "Planchas", 
                                  10, proveedor_aluminios, 25.00, "importado",
                                  {"impuesto": 0.15})

        sistema.registrar_ingreso("NA001", 30, "compra")  # Solo 30, menos del mínimo que es 50
        sistema.registrar_ingreso("IM001", 2, "compra")   # Solo 2, menos del mínimo que es 3
        sistema.registrar_ingreso("NA002", 200, "compra") # 200, más del mínimo que es 100
        sistema.registrar_ingreso("IM002", 5, "compra")   # 5, menos del mínimo que es10

    except (CodigoDuplicado, ValueError) as e:
        print(f"Error en datos de ejemplo: {e}")
    except Exception as e:
        print(f"Error inesperado en datos de ejemplo: {e}")

    menu = MenuSistema()
    menu.mostrar_menu()

if __name__ == "__main__":
    main()