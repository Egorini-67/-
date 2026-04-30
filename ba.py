import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageFilter

class ImageBlurrer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Blurrer")

        # Создаём фрейм для управления
        control_frame = tk.Frame(root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Виджет для выбора степени размытия
        tk.Label(control_frame, text="Blur radius:").pack(side=tk.LEFT)
        self.blur_radius = tk.IntVar(value=10)
        blur_scale = ttk.Scale(
            control_frame,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.blur_radius
        )
        blur_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        # Отображение текущего значения
        self.radius_label = tk.Label(control_frame, text="10 px")
        self.radius_label.pack(side=tk.LEFT)

        # Обновляем метку при изменении ползунка
        blur_scale.config(command=self.update_radius_label)

        self.canvas = tk.Canvas(root, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.tk_image = None
        self.image_id = None
        self.blurred_areas = []
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
        file_menu = tk.Menu(self.menu)
        file_menu.add_command(label="Open Image", command=self.load_image)
        file_menu.add_command(label="Save Image", command=self.save_image)
        self.menu.add_cascade(label="File", menu=file_menu)

    def update_radius_label(self, value):
        """Обновляет метку с текущим значением радиуса размытия"""
        self.radius_label.config(text=f"{int(float(value))} px")

    def resize_image_to_fit(self, max_width=1200, max_height=800):
        """Масштабирует изображение, чтобы оно поместилось в заданные размеры"""
        img_width, img_height = self.image.size

        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))
            self.image = self.image.resize(new_size, Image.Resampling.LANCZOS)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if file_path:
            self.image = Image.open(file_path)
            self.resize_image_to_fit()  # Масштабируем под окно
            self.display_image()

    def save_image(self):
        """Сохраняет текущее изображение"""
        if self.image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
            )
            if file_path:
                self.image.save(file_path)

    def display_image(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.update()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        if self.image:
            self.canvas.delete("rect")
            self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
                outline="red", tag="rect"
            )

    def on_button_release(self, event):
        if self.image and self.start_x is not None and self.start_y is not None:
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y

            # Сортируем координаты для корректного выделения
            x1, x2 = sorted((x1, x2))
            y1, y2 = sorted((y1, y2))

            self.blurred_areas.append((x1, y1, x2, y2))
            self.blur_area(x1, y1, x2, y2)
            self.start_x = None
            self.start_y = None

    def blur_area(self, x1, y1, x2, y2):
        """Размывает указанную область с текущим радиусом размытия"""
        blurred_image = self.image.copy()
        # Извлекаем область для размытия
        area = blurred_image.crop((x1, y1, x2, y2))
        # Применяем размытие с выбранным радиусом
        blurred_area = area.filter(ImageFilter.GaussianBlur(self.blur_radius.get()))
        # Вставляем размытую область обратно
        blurred_image.paste(blurred_area, (x1, y1))

        # Обновляем исходное изображение и отображение
        self.image = blurred_image
        self.tk_image = ImageTk.PhotoImage(blurred_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.update()

# Запуск приложения
root = tk.Tk()
app = ImageBlurrer(root)
root.mainloop()





