const API = 'http://127.0.0.1:5000/api';
let token = localStorage.getItem('token') || '';
let userRol = '';
let modoEdicion = false;
let idProductoEditando = null;

const modalProducto = new bootstrap.Modal(document.getElementById('modalProducto'));

document.addEventListener('DOMContentLoaded', () => {
  const authSection = document.getElementById('auth-section');
  const appSection = document.getElementById('app-section');
  const loginForm = document.getElementById('login-form');
  const logoutBtn = document.getElementById('logout-btn');
  const nuevoBtn = document.getElementById('nuevo-producto');
  const exportBtn = document.getElementById('exportar-btn');
  const tabla = document.getElementById('tabla-productos');
  const userRoleDisplay = document.getElementById('user-role');
  const formProducto = document.getElementById('form-producto');

  if (token) {
    cargarProductos();
    authSection.style.display = 'none';
    appSection.style.display = 'block';
    logoutBtn.style.display = 'inline-block';
    obtenerRol();
  }

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (res.ok) {
      token = data.access_token;
      userRol = data.rol;
      localStorage.setItem('token', token);
      cargarProductos();
      authSection.style.display = 'none';
      appSection.style.display = 'block';
      logoutBtn.style.display = 'inline-block';
      userRoleDisplay.textContent = `Rol: ${userRol}`;
    } else {
      Swal.fire('Error', data.message, 'error');
    }
  });

  logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    location.reload();
  });

  nuevoBtn.addEventListener('click', () => {
    modoEdicion = false;
    formProducto.reset();
    modalProducto.show();
  });

  exportBtn.addEventListener('click', async () => {
    try {
      const res = await fetch(`${API}/productos/exportar`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Error al exportar');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'productos.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      Swal.fire('Error', 'No se pudo exportar el archivo', 'error');
    }
  });

  formProducto.addEventListener('submit', async (e) => {
    e.preventDefault();
    const producto = {
      codigo: document.getElementById('codigo').value,
      nombre: document.getElementById('nombre').value,
      marca: document.getElementById('marca').value,
      precio: parseFloat(document.getElementById('precio').value) || 0,
      stock: parseInt(document.getElementById('stock').value) || 0
    };

    console.log("Producto a enviar:", producto); // 

    const url = modoEdicion ? `${API}/productos/${idProductoEditando}` : `${API}/productos/`;
    const method = modoEdicion ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(producto)
    });

    if (res.ok) {
      Swal.fire('Éxito', modoEdicion ? 'Producto actualizado' : 'Producto creado', 'success');
      modalProducto.hide();
      cargarProductos();
    } else {
      const err = await res.json().catch(() => ({ error: 'Error inesperado del servidor' }));
      Swal.fire('Error', err.error || 'Error al guardar el producto', 'error');
    }
  });

  async function cargarProductos() {
    const res = await fetch(`${API}/productos`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const json = await res.json();
    renderizarProductos(json.productos);
  }

  function renderizarProductos(productos) {
    tabla.innerHTML = '';
    productos.forEach(p => {
      const fila = document.createElement('tr');
      fila.innerHTML = `
        <td>${p.id}</td>
        <td>${p.codigo}</td>
        <td>${p.nombre}</td>
        <td>${p.marca}</td>
        <td>${p.precio}</td>
        <td>${p.stock}</td>
        <td>
          ${userRol === 'admin' ? `
            <button class="btn btn-sm btn-warning me-1" data-id="${p.id}" data-action="editar">Editar</button>
            <button class="btn btn-sm btn-danger" data-id="${p.id}" data-action="eliminar">Eliminar</button>` : ''}
        </td>
      `;
      tabla.appendChild(fila);
    });
    asignarEventosAcciones();
  }

  function asignarEventosAcciones() {
    tabla.querySelectorAll('button[data-action="editar"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        editarProducto(id);
      });
    });
    tabla.querySelectorAll('button[data-action="eliminar"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        eliminarProducto(id);
      });
    });
  }

  async function editarProducto(id) {
    const res = await fetch(`${API}/productos`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const json = await res.json();
    const producto = json.productos.find(p => p.id == id);
    if (producto) {
      modoEdicion = true;
      idProductoEditando = producto.id;
      document.getElementById('codigo').value = producto.codigo;
      document.getElementById('nombre').value = producto.nombre;
      document.getElementById('marca').value = producto.marca;
      document.getElementById('precio').value = producto.precio;
      document.getElementById('stock').value = producto.stock;
      modalProducto.show();
    }
  }

  async function eliminarProducto(id) {
    const confirm = await Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esto eliminará el producto permanentemente.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Sí, eliminar'
    });

    if (confirm.isConfirmed) {
      const res = await fetch(`${API}/productos/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        Swal.fire('Eliminado', 'Producto eliminado correctamente', 'success');
        cargarProductos();
      } else {
        Swal.fire('Error', 'No se pudo eliminar el producto', 'error');
      }
    }
  }

  async function obtenerRol() {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();
    userRoleDisplay.textContent = `Rol: ${data.rol || 'usuario'}`;
  }
});
