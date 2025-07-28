import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from datetime import datetime, date
import json
import os

# Configurar estilo de matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ExpenseManager:
    """Gestor de gastos mejorado con pandas y persistencia de datos"""
    
    def __init__(self, salary=0.0):
        self.salary = salary
        self.categories = [
            "Comida", "Transporte", "Educación", "Diversión", "Deporte",
            "Servicios Básicos", "Viajes", "Ropa", "Compras en Línea", "Otros"
        ]
        self.data_file = "expenses_data.json"
        self.expenses_df = self.load_data()
    
    def load_data(self):
        """Carga datos desde archivo JSON o crea DataFrame vacío"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('expenses'):
                        df = pd.DataFrame(data['expenses'])
                        df['date'] = pd.to_datetime(df['date'])
                        self.salary = data.get('salary', 0.0)
                        return df
            except Exception as e:
                messagebox.showwarning("Advertencia", f"Error al cargar datos: {e}")
        
        return pd.DataFrame(columns=['category', 'amount', 'date', 'description'])
    
    def save_data(self):
        """Guarda datos en archivo JSON"""
        try:
            data = {
                'salary': self.salary,
                'expenses': self.expenses_df.to_dict('records') if not self.expenses_df.empty else []
            }
            # Convertir fechas a string para JSON
            for expense in data['expenses']:
                expense['date'] = expense['date'].isoformat() if hasattr(expense['date'], 'isoformat') else str(expense['date'])
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {e}")
    
    def add_expense(self, category, amount, description=""):
        """Añade un nuevo gasto usando pandas"""
        new_expense = pd.DataFrame([{
            'category': category,
            'amount': amount,
            'date': datetime.now(),
            'description': description
        }])
        self.expenses_df = pd.concat([self.expenses_df, new_expense], ignore_index=True)
        self.save_data()
    
    def get_statistics(self, period='month'):
        """Obtiene estadísticas usando operaciones pandas optimizadas"""
        if self.expenses_df.empty:
            return pd.Series(dtype=float), 0.0, self.salary
        
        # Filtrar por período
        today = datetime.now()
        if period == 'month':
            mask = (self.expenses_df['date'].dt.month == today.month) & \
                   (self.expenses_df['date'].dt.year == today.year)
        else:  # all time
            mask = pd.Series([True] * len(self.expenses_df))
        
        filtered_df = self.expenses_df[mask]
        
        if filtered_df.empty:
            return pd.Series(dtype=float), 0.0, self.salary
        
        # Agrupar por categoría usando pandas
        category_totals = filtered_df.groupby('category')['amount'].sum()
        total_expenses = category_totals.sum()
        balance = self.salary - total_expenses
        
        return category_totals, total_expenses, balance
    
    def get_monthly_trends(self):
        """Obtiene tendencias mensuales de gastos"""
        if self.expenses_df.empty:
            return pd.Series(dtype=float)
        
        monthly_expenses = self.expenses_df.groupby(
            self.expenses_df['date'].dt.to_period('M')
        )['amount'].sum()
        return monthly_expenses

class ModernExpenseApp:
    """Interfaz moderna y mejorada para gestión de gastos"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.initialize_salary()
        self.manager = ExpenseManager(self.salary)
        self.setup_ui()
    
    def setup_window(self):
        """Configuración inicial de la ventana"""
        self.root.title("💰 Gestor de Gastos Inteligente")
        self.root.geometry("500x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Personalizar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Accent.TButton', background='#4CAF50', foreground='white')
        style.configure('Category.TButton', padding=(10, 5))
    
    def initialize_salary(self):
        """Inicializa el sueldo del usuario"""
        self.salary = simpledialog.askfloat(
            "Configuración Inicial", 
            "Ingrese su sueldo mensual:",
            minvalue=0.0
        ) or 0.0
    
    def setup_ui(self):
        """Configura la interfaz de usuario moderna"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sistema de Gestión de Gastos", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para información del sueldo
        info_frame = ttk.LabelFrame(main_frame, text="Información Personal", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        salary_label = ttk.Label(info_frame, text=f"💵 Sueldo Mensual: ${self.salary:.2f}")
        salary_label.pack()
        
        ttk.Button(
            info_frame, 
            text="Actualizar Sueldo", 
            command=self.update_salary
        ).pack(pady=5)
        
        # Frame para categorías
        categories_frame = ttk.LabelFrame(main_frame, text="Agregar Gastos por Categoría", padding="10")
        categories_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de botones de categorías (2 columnas)
        for idx, category in enumerate(self.manager.categories):
            row, col = divmod(idx, 2)
            ttk.Button(
                categories_frame,
                text=f"🏷️ {category}",
                style='Category.TButton',
                command=lambda c=category: self.add_expense_dialog(c)
            ).grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configurar columnas para expansion
        categories_frame.grid_columnconfigure(0, weight=1)
        categories_frame.grid_columnconfigure(1, weight=1)
        
        # Botones de acción
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="📊 Ver Estadísticas del Mes",
            style='Accent.TButton',
            command=lambda: self.show_statistics('month')
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            actions_frame,
            text="📈 Ver Estadísticas Generales",
            command=lambda: self.show_statistics('all')
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            actions_frame,
            text="🗑️ Limpiar Datos",
            command=self.clear_data
        ).pack(fill=tk.X, pady=2)
    
    def update_salary(self):
        """Actualiza el sueldo del usuario"""
        new_salary = simpledialog.askfloat(
            "Actualizar Sueldo", 
            f"Sueldo actual: ${self.salary:.2f}\nIngrese nuevo sueldo:",
            minvalue=0.0
        )
        if new_salary is not None:
            self.salary = new_salary
            self.manager.salary = new_salary
            self.manager.save_data()
            self.setup_ui()  # Refresh UI
    
    def add_expense_dialog(self, category):
        """Diálogo mejorado para agregar gastos"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Agregar Gasto - {category}")
        dialog.geometry("350x200")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Categoría: {category}", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        ttk.Label(frame, text="Monto:").pack(anchor='w', pady=(10, 0))
        amount_var = tk.DoubleVar()
        amount_entry = ttk.Entry(frame, textvariable=amount_var, width=20)
        amount_entry.pack(fill=tk.X, pady=(0, 10))
        amount_entry.focus()
        
        ttk.Label(frame, text="Descripción (opcional):").pack(anchor='w')
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(frame, textvariable=desc_var, width=20)
        desc_entry.pack(fill=tk.X, pady=(0, 20))
        
        def save_expense():
            amount = amount_var.get()
            if amount > 0:
                self.manager.add_expense(category, amount, desc_var.get())
                messagebox.showinfo("Éxito", f"Gasto de ${amount:.2f} agregado en {category}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Ingrese un monto válido")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Guardar", command=save_expense).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: save_expense())
    
    def show_statistics(self, period):
        """Muestra estadísticas en ventana moderna con gráficos mejorados"""
        category_totals, total_expenses, balance = self.manager.get_statistics(period)
        
        if category_totals.empty:
            messagebox.showinfo("Sin Datos", "No hay gastos registrados para mostrar")
            return
        
        # Crear ventana de estadísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"📊 Estadísticas - {period.title()}")
        stats_window.geometry("900x700")
        stats_window.configure(bg='#f0f0f0')
        
        # Notebook para pestañas
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de resumen
        self.create_summary_tab(notebook, total_expenses, balance, period)
        
        # Pestaña de gráficos
        self.create_charts_tab(notebook, category_totals, period)
        
        # Pestaña de detalles
        self.create_details_tab(notebook, period)
    
    def create_summary_tab(self, notebook, total_expenses, balance, period):
        """Crea la pestaña de resumen"""
        summary_frame = ttk.Frame(notebook, padding="20")
        notebook.add(summary_frame, text="📋 Resumen")
        
        # Información general
        info_text = f"""
💰 Sueldo Mensual: ${self.manager.salary:.2f}
💸 Total Gastado ({period}): ${total_expenses:.2f}
💵 Balance: ${balance:.2f}
📊 Porcentaje Gastado: {(total_expenses/self.manager.salary*100):.1f}%
        """.strip()
        
        info_label = ttk.Label(summary_frame, text=info_text, font=('Courier', 12))
        info_label.pack(anchor='w', pady=(0, 20))
        
        # Indicador de estado
        status_color = 'green' if balance >= 0 else 'red'
        status_text = "✅ Dentro del presupuesto" if balance >= 0 else "⚠️ Exceso en gastos"
        
        status_label = tk.Label(
            summary_frame, 
            text=status_text, 
            fg=status_color, 
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        )
        status_label.pack(pady=10)
    
    def create_charts_tab(self, notebook, category_totals, period):
        """Crea la pestaña de gráficos"""
        charts_frame = ttk.Frame(notebook, padding="10")
        notebook.add(charts_frame, text="📈 Gráficos")
        
        # Crear figura con subplots
        fig = Figure(figsize=(12, 8), dpi=100)
        
        # Gráfico de barras
        ax1 = fig.add_subplot(221)
        category_totals.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('Gastos por Categoría')
        ax1.set_ylabel('Monto ($)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Gráfico de torta
        ax2 = fig.add_subplot(222)
        category_totals.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
        ax2.set_title('Distribución de Gastos')
        ax2.set_ylabel('')
        
        # Tendencia mensual
        monthly_trends = self.manager.get_monthly_trends()
        if not monthly_trends.empty:
            ax3 = fig.add_subplot(212)
            monthly_trends.plot(kind='line', ax=ax3, marker='o', color='green')
            ax3.set_title('Tendencia de Gastos Mensuales')
            ax3.set_ylabel('Monto ($)')
            ax3.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_details_tab(self, notebook, period):
        """Crea la pestaña de detalles con tabla"""
        details_frame = ttk.Frame(notebook, padding="10")
        notebook.add(details_frame, text="📝 Detalles")
        
        # Crear tabla
        columns = ('Fecha', 'Categoría', 'Monto', 'Descripción')
        tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Filtrar y mostrar datos
        df = self.manager.expenses_df
        if not df.empty:
            if period == 'month':
                today = datetime.now()
                mask = (df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)
                filtered_df = df[mask]
            else:
                filtered_df = df
            
            # Ordenar por fecha descendente
            filtered_df = filtered_df.sort_values('date', ascending=False)
            
            for _, row in filtered_df.iterrows():
                tree.insert('', tk.END, values=(
                    row['date'].strftime('%Y-%m-%d %H:%M'),
                    row['category'],
                    f"${row['amount']:.2f}",
                    row['description'] or '-'
                ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def clear_data(self):
        """Limpia todos los datos con confirmación"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar todos los gastos?"):
            self.manager.expenses_df = pd.DataFrame(columns=['category', 'amount', 'date', 'description'])
            self.manager.save_data()
            messagebox.showinfo("Éxito", "Todos los datos han sido eliminados")

def main():
    """Función principal"""
    root = tk.Tk()
    app = ModernExpenseApp(root)
    
    # Manejar cierre de ventana
    def on_closing():
        app.manager.save_data()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()