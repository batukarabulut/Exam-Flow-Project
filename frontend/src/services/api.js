// src/services/api.js
import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/update/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getDepartments: () => api.get('/auth/departments/'),
  getUsers: (params) => api.get('/auth/users/', { params }),
};

// Room API calls
export const roomAPI = {
  getRooms: (params) => api.get('/rooms/', { params }),
  createRoom: (roomData) => api.post('/rooms/', roomData),
  updateRoom: (id, roomData) => api.put(`/rooms/${id}/`, roomData),
  deleteRoom: (id) => api.delete(`/rooms/${id}/`),
  checkAvailability: (data) => api.post('/rooms/check-availability/', data),
  getRoomSchedule: (roomId, params) => api.get(`/rooms/${roomId}/schedule/`, { params }),
  getBuildings: () => api.get('/rooms/buildings/'),
  createBuilding: (buildingData) => api.post('/rooms/buildings/', buildingData),
};

// Exam API calls
export const examAPI = {
  getExams: (params) => api.get('/exams/', { params }),
  createExam: (examData) => api.post('/exams/', examData),
  updateExam: (id, examData) => api.put(`/exams/${id}/`, examData),
  deleteExam: (id) => api.delete(`/exams/${id}/`),
  getMyExams: () => api.get('/exams/my-exams/'),
  checkConflicts: (data) => api.post('/exams/check-conflicts/', data),
  getDepartmentSchedule: (departmentId, params) => api.get(`/exams/department/${departmentId}/schedule/`, { params }),
  getCourses: (params) => api.get('/exams/courses/', { params }),
  createCourse: (courseData) => api.post('/exams/courses/', courseData),
};

// Notification API calls
export const notificationAPI = {
  getNotifications: (params) => api.get('/notifications/', { params }),
  markAsRead: (id) => api.post(`/notifications/${id}/mark-read/`),
  markAllAsRead: () => api.post('/notifications/mark-all-read/'),
  getUnreadCount: () => api.get('/notifications/unread-count/'),
  getSummary: () => api.get('/notifications/summary/'),
};

export default api;