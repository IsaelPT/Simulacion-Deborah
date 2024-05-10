class Rutas:
    """Para variables con rutas estáticas para cargar componentes necesarios."""

    MAINWINDOW_UI = "qt_ui/main_window_v2.ui"
    SIMULATIONWIDGET_UI = "qt_ui/simulation_widget.ui"


class Estilos:
    """
    Contiene estilos personalizados que se utilizan en botones y otros componentes
    en las diversas interfaces gráficas.
    """

    botones = {
        "botones_acciones_verdes": """
            QPushButton {
                background-color: #b2f2bb;
                border: 1px solid #8f8f91;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8f8f91;
            }
        """,
    }
    """Para botones `Comenzar Simulacion`, `Detener Simulacion`, `Salir` y otros."""
