const API_URL = '/api/auth';

function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form-section').forEach(f => f.classList.remove('active'));
    
    if (tab === 'login') {
        document.querySelectorAll('.tab')[0].classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } else {
        document.querySelectorAll('.tab')[1].classList.add('active');
        document.getElementById('registerForm').classList.add('active');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const phone = document.getElementById('loginPhone').value;
    const password = document.getElementById('loginPassword').value;
    const errorEl = document.getElementById('loginError');
    const btn = document.getElementById('loginBtn');
    
    errorEl.textContent = '';
    btn.textContent = 'Kutilmoqda...';
    btn.disabled = true;

    try {
        const formData = new URLSearchParams();
        formData.append('username', phone);
        formData.append('password', password);

        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await res.json();
        
        if (res.ok) {
            localStorage.setItem('token', data.access_token);
            await loadProfile();
        } else {
            errorEl.textContent = data.detail || 'Xatolik yuz berdi';
        }
    } catch (err) {
        errorEl.textContent = 'Tarmoq xatosi';
    } finally {
        btn.textContent = 'Tizimga kirish';
        btn.disabled = false;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const firstName = document.getElementById('regFirstName').value;
    const lastName = document.getElementById('regLastName').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const errorEl = document.getElementById('regError');
    const btn = document.getElementById('regBtn');
    
    errorEl.textContent = '';
    btn.textContent = 'Kutilmoqda...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                phone_number: phone,
                password: password
            })
        });

        const data = await res.json();
        
        if (res.ok) {
            document.getElementById('loginPhone').value = phone;
            document.getElementById('loginPassword').value = password;
            switchTab('login');
            alert("Muvaffaqiyatli ro'yxatdan o'tdingiz. Tizimga kirishingiz mumkin!");
            document.getElementById('registerForm').reset();
        } else {
            errorEl.textContent = data.detail || 'Xatolik yuz berdi';
        }
    } catch (err) {
        errorEl.textContent = 'Tarmoq xatosi';
    } finally {
        btn.textContent = "Ro'yxatdan o'tish";
        btn.disabled = false;
    }
}

async function loadProfile() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (res.ok) {
            const user = await res.json();
            document.getElementById('authTabs').style.display = 'none';
            document.getElementById('loginForm').classList.remove('active');
            document.getElementById('registerForm').classList.remove('active');
            
            document.getElementById('dashboard').classList.add('active');
            document.getElementById('userName').textContent = `${user.first_name} ${user.last_name}`;
            document.getElementById('userPhone').textContent = user.phone_number;
            document.getElementById('userInitial').textContent = user.first_name.charAt(0).toUpperCase();

            // Load extra data
            await loadDoctors();
            await loadAppointments();
        } else {
            localStorage.removeItem('token');
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadDoctors() {
    const res = await fetch(`/api/doctors/`);
    if(res.ok) {
        const doctors = await res.json();
        const container = document.getElementById('doctorsList');
        container.innerHTML = '';
        doctors.forEach(doc => {
            const card = document.createElement('div');
            card.className = 'doctor-card';
            
            const now = new Date();
            now.setMinutes(now.getMinutes() + 30 - (now.getMinutes() % 30)); // next 30 min block
            
            // Fix timezone issue for datetime-local
            const tzoffset = now.getTimezoneOffset() * 60000;
            const localISOTime = (new Date(now - tzoffset)).toISOString().slice(0,16);

            card.innerHTML = `
                <div class="doc-header">
                    <div class="doc-avatar">${doc.image_url || '👨‍⚕️'}</div>
                    <div class="doc-info">
                        <h4>${doc.first_name} ${doc.last_name}</h4>
                        <p>${doc.specialty} • ${doc.experience_years} yil tajriba</p>
                    </div>
                </div>
                <form class="book-form" onsubmit="bookAppointment(event, ${doc.id})">
                    <input type="datetime-local" id="date-${doc.id}" required value="${localISOTime}" min="${localISOTime}">
                    <button type="submit" class="book-btn">Yozilish</button>
                </form>
            `;
            container.appendChild(card);
        });
    }
}

async function bookAppointment(e, doctorId) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    const dateInput = document.getElementById(`date-${doctorId}`).value;
    
    try {
        const res = await fetch(`/api/appointments/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doctor_id: doctorId,
                appointment_date: dateInput
            })
        });
        if(res.ok) {
            alert("Muvaffaqiyatli qabulga yozildingiz!");
            await loadAppointments();
        } else {
            const data = await res.json();
            alert("Xatolik: " + data.detail);
        }
    } catch(err) {
        console.error(err);
    }
}

async function loadAppointments() {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/appointments/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if(res.ok) {
        const appointments = await res.json();
        const container = document.getElementById('appointmentsList');
        container.innerHTML = '';
        if(appointments.length === 0) {
            container.innerHTML = '<p style="color: #64748b; font-size: 14px;">Hali qabulga yozilmagansiz.</p>';
            return;
        }
        appointments.forEach(app => {
            const date = new Date(app.appointment_date).toLocaleString('uz-UZ', {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute:'2-digit'
            });
            const statusMap = {
                'pending': 'Kutilmoqda',
                'confirmed': 'Tasdiqlangan',
                'cancelled': 'Bekor qilingan'
            };
            const card = document.createElement('div');
            card.className = 'appointment-card';
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="doc-info">
                        <h4>${app.doctor.first_name} ${app.doctor.last_name}</h4>
                        <p>${app.doctor.specialty} • ${date}</p>
                    </div>
                    <span class="status-badge status-${app.status}">${statusMap[app.status] || app.status}</span>
                </div>
            `;
            container.appendChild(card);
        });
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    document.getElementById('authTabs').style.display = 'flex';
    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('loginPassword').value = '';
    switchTab('login');
}

document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
});
