#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Avanzado de Gestión de Inventario (POO + Colecciones + SQLite)
Dominio: tienda genérica (ferretería, panadería, librería, etc.)

- Clase Producto con validaciones (ID, nombre, cantidad, precio, categoría).
- Clase Inventario que usa colecciones (dict, list, set, tuple) y persiste en SQLite.
- CRUD completo: añadir, eliminar, actualizar, buscar, listar.
- Menú de consola para interactuar con el inventario.

Requisitos: Python 3.9+
Ejecución: python inventario_poo_sqlite.py
"""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Iterable

DB_NAME = "inventario.db"


# ----------------------------
# Modelo: Producto (POO)
# ----------------------------
@dataclass(eq=True, frozen=False)
class Producto:
    id: int
    nombre: str
    cantidad: int
    precio: float
    categoria: str = field(default="General")

    # Validaciones a través de propiedades que escriben en atributos internos _id/_nombre/_cantidad/_precio
    @property
    def id(self) -> int:  # type: ignore[override]
        return self._id  # type: ignore[attr-defined]

    @id.setter
    def id(self, value: int) -> None:  # type: ignore[override]
        if not isinstance(value, int) or value <= 0:
            raise ValueError("El ID debe ser un entero > 0 y único.")
        self._id = value  # type: ignore[attr-defined]

    @property
    def nombre(self) -> str:  # type: ignore[override]
        return self._nombre  # type: ignore[attr-defined]

    @nombre.setter
    def nombre(self, value: str) -> None:  # type: ignore[override]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = value.strip()  # type: ignore[attr-defined]

    @property
    def cantidad(self) -> int:  # type: ignore[override]
        return self._cantidad  # type: ignore[attr-defined]

    @cantidad.setter
    def cantidad(self, value: int) -> None:  # type: ignore[override]
        if not isinstance(value, int) or value < 0:
            raise ValueError("La cantidad debe ser un entero >= 0.")
        self._cantidad = value  # type: ignore[attr-defined]

    @property
    def precio(self) -> float:  # type: ignore[override]
        return self._precio  # type: ignore[attr-defined]

    @precio.setter
    def precio(self, value: float) -> None:  # type: ignore[override]
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("El precio debe ser un número >= 0.")
        self._precio = float(value)  # type: ignore[attr-defined]

    def to_row(self) -> tuple:
        """Tupla ordenada para SQLite."""
        return (self.id, self.nombre, self.cantidad, self.precio, self.categoria)

    @staticmethod
    def from_row(row: tuple) -> "Producto":
        pid, nombre, cantidad, precio, categoria = row
        return Producto(id=pid, nombre=nombre, cantidad=cantidad, precio=precio, categoria=categoria)


# --------------------------------------
# Servicio/Repositorio: Inventario (POO)
# --------------------------------------
class Inventario:
    """
    Gestiona una colección de productos con acceso rápido por ID (dict) y persistencia en SQLite.
    """

    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._conn = sqlite3.connect(self.db_name)
        self._conn.row_factory = sqlite3.Row
        self._crear_tabla_si_no_existe()
        # Colección principal: dict para acceso O(1) por ID
        self.productos: Dict[int, Producto] = {}
        self._cargar_desde_bd()

    # ------------------ Persistencia ------------------
    def _crear_tabla_si_no_existe(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                    precio REAL NOT NULL CHECK (precio >= 0),
                    categoria TEXT NOT NULL DEFAULT 'General'
                );
                """
            )
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre);")

    def _cargar_desde_bd(self) -> None:
        cur = self._conn.cursor()
        cur.execute("SELECT id, nombre, cantidad, precio, categoria FROM productos")
        for r in cur.fetchall():
            p = Producto.from_row((r["id"], r["nombre"], r["cantidad"], r["precio"], r["categoria"]))
            self.productos[p.id] = p

    def _insertar_bd(self, p: Producto) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO productos (id, nombre, cantidad, precio, categoria) VALUES (?, ?, ?, ?, ?)",
                p.to_row(),
            )

    def _actualizar_bd(self, p: Producto) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE productos SET nombre=?, cantidad=?, precio=?, categoria=? WHERE id=?",
                (p.nombre, p.cantidad, p.precio, p.categoria, p.id),
            )

    def _eliminar_bd(self, pid: int) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM productos WHERE id=?", (pid,))

    # ------------------ Operaciones CRUD ------------------
    def agregar_producto(self, producto: Producto) -> None:
        if producto.id in self.productos:
            raise ValueError(f"Ya existe un producto con ID {producto.id}")
        self.productos[producto.id] = producto
        self._insertar_bd(producto)

    def eliminar_producto(self, pid: int) -> None:
        if pid not in self.productos:
            raise KeyError(f"No existe producto con ID {pid}")
        del self.productos[pid]
        self._eliminar_bd(pid)

    def actualizar_cantidad(self, pid: int, nueva_cantidad: int) -> None:
        p = self.obtener_por_id(pid)
        p.cantidad = nueva_cantidad
        self._actualizar_bd(p)

    def actualizar_precio(self, pid: int, nuevo_precio: float) -> None:
        p = self.obtener_por_id(pid)
        p.precio = nuevo_precio
        self._actualizar_bd(p)

    def actualizar_nombre(self, pid: int, nuevo_nombre: str) -> None:
        p = self.obtener_por_id(pid)
        p.nombre = nuevo_nombre
        self._actualizar_bd(p)

    def actualizar_categoria(self, pid: int, nueva_categoria: str) -> None:
        p = self.obtener_por_id(pid)
        p.categoria = nueva_categoria
        self._actualizar_bd(p)

    # ------------------ Consultas ------------------
    def obtener_por_id(self, pid: int) -> Producto:
        if pid not in self.productos:
            raise KeyError(f"No existe producto con ID {pid}")
        return self.productos[pid]

    def buscar_por_nombre(self, termino: str) -> List[Producto]:
        termino = termino.strip().lower()
        # En memoria: list comprehension + lower (O(n))
        encontrados: List[Producto] = [p for p in self.productos.values() if termino in p.nombre.lower()]
        # En BD: LIKE (útil si hay muchísimos registros), se combinan evitando duplicados con un set de IDs
        cur = self._conn.cursor()
        cur.execute(
            "SELECT id, nombre, cantidad, precio, categoria FROM productos WHERE lower(nombre) LIKE ?",
            (f"%{termino}%",),
        )
        ids_vistos = {p.id for p in encontrados}
        for r in cur.fetchall():
            if r["id"] not in ids_vistos:
                encontrados.append(Producto.from_row((r["id"], r["nombre"], r["cantidad"], r["precio"], r["categoria"])))
                ids_vistos.add(r["id"])
        return encontrados

    def listar_todos(self) -> List[Producto]:
        # Orden por ID usando sorted (list) y una lambda
        return sorted(self.productos.values(), key=lambda p: p.id)

    # ------------------ Utilidades de colección ------------------
    def stock_total(self) -> int:
        return sum(p.cantidad for p in self.productos.values())

    def productos_sin_stock(self) -> List[Producto]:
        return [p for p in self.productos.values() if p.cantidad == 0]

    def categorias_disponibles(self) -> List[str]:
        # set para evitar repetidos, luego lo convertimos a lista ordenada (list + sorted)
        return sorted({p.categoria for p in self.productos.values()})

    def cerrar(self) -> None:
        self._conn.close()


# ----------------------------
# Interfaz de Usuario (CLI)
# ----------------------------
def imprimir_producto(p: Producto) -> None:
    print(f"ID: {p.id} | Nombre: {p.nombre} | Cantidad: {p.cantidad} | Precio: ${p.precio:,.2f} | Categoría: {p.categoria}")


def menu() -> None:
    inv = Inventario()
    print("\n=== Sistema de Inventario (SQLite) ===")
    print("Base de datos:", inv.db_name)
    try:
        while True:
            print("\nSeleccione una opción:")
            print("1) Añadir producto")
            print("2) Eliminar producto")
            print("3) Actualizar cantidad")
            print("4) Actualizar precio")
            print("5) Actualizar nombre")
            print("6) Actualizar categoría")
            print("7) Buscar por nombre")
            print("8) Mostrar todos")
            print("9) Estadísticas (stock total, sin stock, categorías)")
            print("0) Salir")
            opcion = input("> ").strip()

            try:
                if opcion == "1":
                    pid = int(input("ID (entero > 0): ").strip())
                    nombre = input("Nombre: ").strip()
                    cantidad = int(input("Cantidad (>=0): ").strip())
                    precio = float(input("Precio (>=0): ").strip())
                    categoria = input("Categoría (opcional, Enter=General): ").strip() or "General"
                    p = Producto(id=pid, nombre=nombre, cantidad=cantidad, precio=precio, categoria=categoria)
                    inv.agregar_producto(p)
                    print("✔ Producto añadido.")

                elif opcion == "2":
                    pid = int(input("ID a eliminar: ").strip())
                    inv.eliminar_producto(pid)
                    print("✔ Producto eliminado.")

                elif opcion == "3":
                    pid = int(input("ID: ").strip())
                    nueva_cantidad = int(input("Nueva cantidad: ").strip())
                    inv.actualizar_cantidad(pid, nueva_cantidad)
                    print("✔ Cantidad actualizada.")

                elif opcion == "4":
                    pid = int(input("ID: ").strip())
                    nuevo_precio = float(input("Nuevo precio: ").strip())
                    inv.actualizar_precio(pid, nuevo_precio)
                    print("✔ Precio actualizado.")

                elif opcion == "5":
                    pid = int(input("ID: ").strip())
                    nuevo_nombre = input("Nuevo nombre: ").strip()
                    inv.actualizar_nombre(pid, nuevo_nombre)
                    print("✔ Nombre actualizado.")

                elif opcion == "6":
                    pid = int(input("ID: ").strip())
                    nueva_categoria = input("Nueva categoría: ").strip() or "General"
                    inv.actualizar_categoria(pid, nueva_categoria)
                    print("✔ Categoría actualizada.")

                elif opcion == "7":
                    termino = input("Buscar (por nombre): ").strip()
                    resultados = inv.buscar_por_nombre(termino)
                    if resultados:
                        print(f"\nResultados ({len(resultados)}):")
                        for p in resultados:
                            imprimir_producto(p)
                    else:
                        print("No se encontraron coincidencias.")

                elif opcion == "8":
                    todos = inv.listar_todos()
                    if not todos:
                        print("Inventario vacío.")
                    else:
                        print("\nInventario:")
                        for p in todos:
                            imprimir_producto(p)

                elif opcion == "9":
                    print(f"Stock total: {inv.stock_total()}")
                    sin = inv.productos_sin_stock()
                    if sin:
                        print("Sin stock:")
                        for p in sin:
                            imprimir_producto(p)
                    else:
                        print("No hay productos sin stock.")
                    print("Categorías disponibles:", ", ".join(inv.categorias_disponibles()) or "(ninguna)")

                elif opcion == "0":
                    print("Hasta pronto 👋")
                    break
                else:
                    print("Opción no válida. Intente de nuevo.")

            except (ValueError, KeyError) as e:
                print(f"⚠ Error: {e}")
    finally:
        inv.cerrar()


if __name__ == "__main__":
    menu()
