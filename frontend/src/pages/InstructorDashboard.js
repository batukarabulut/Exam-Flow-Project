// src/pages/InstructorDashboard.js
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  AppBar,
  Toolbar,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Avatar,
  Tab,
  Tabs,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  School,
  Add,
  Event,
  Schedule,
  Person,
  Logout,
  CalendarToday,
  Room,
  Edit,
  Delete,
  Visibility
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { examAPI, roomAPI } from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const InstructorDashboard = () => {
  const { user, logout } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [exams, setExams] = useState([]);
  const [courses, setCourses] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openExamDialog, setOpenExamDialog] = useState(false);
  const [editingExam, setEditingExam] = useState(null);
  const [examForm, setExamForm] = useState({
    course: '',
    exam_type: 'midterm',
    date: '',
    start_time: '',
    end_time: '',
    room: '',
    duration_minutes: 120,
    max_students: 50,
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [examsRes, coursesRes, roomsRes] = await Promise.all([
        examAPI.getMyExams(),
        examAPI.getCourses({ instructor: user.id }),
        roomAPI.getRooms()
      ]);
      
      setExams(examsRes.data || []);
      setCourses(coursesRes.data.results || coursesRes.data || []);
      setRooms(roomsRes.data.results || roomsRes.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleCreateExam = () => {
    setEditingExam(null);
    setExamForm({
      course: '',
      exam_type: 'midterm',
      date: '',
      start_time: '',
      end_time: '',
      room: '',
      duration_minutes: 120,
      max_students: 50,
      notes: ''
    });
    setOpenExamDialog(true);
  };

  const handleEditExam = (exam) => {
  setEditingExam(exam);
  setExamForm({
    course: exam.course_detail?.code || '',
    exam_type: exam.exam_type,
    date: exam.date,
    start_time: exam.start_time,
    end_time: exam.end_time,
    room: exam.room_detail?.name || '',
    duration_minutes: exam.duration_minutes,
    max_students: exam.max_students,
    notes: exam.notes || ''
  });
  setOpenExamDialog(true);
};

  const handleDeleteExam = async (examId) => {
    if (window.confirm('Are you sure you want to delete this exam?')) {
      try {
        await examAPI.deleteExam(examId);
        fetchData();
        setError('');
      } catch (error) {
        setError('Failed to delete exam');
      }
    }
  };

  const handleExamFormChange = (e) => {
    const { name, value } = e.target;
    setExamForm(prev => ({
      ...prev,
      [name]: value
    }));

    // Auto-calculate end time based on start time and duration
    if (name === 'start_time' || name === 'duration_minutes') {
      const startTime = name === 'start_time' ? value : examForm.start_time;
      const duration = name === 'duration_minutes' ? parseInt(value) : examForm.duration_minutes;
      
      if (startTime && duration) {
        const start = new Date(`2000-01-01T${startTime}`);
        const end = new Date(start.getTime() + duration * 60000);
        const endTime = end.toTimeString().slice(0, 5);
        setExamForm(prev => ({
          ...prev,
          end_time: endTime
        }));
      }
    }
  };

  const handleExamSubmit = async () => {
  try {
    console.log('Submitting exam form data:', examForm);

    if (!examForm.course || !examForm.date || !examForm.start_time || !examForm.room) {
      setError('Please fill in all required fields (Course, Date, Start Time, Room)');
      return;
    }

    const selectedRoom = rooms.find(room => room.name === examForm.room);
    if (selectedRoom && parseInt(examForm.max_students) > selectedRoom.capacity) {
      setError(`Maximum students (${examForm.max_students}) exceeds room capacity (${selectedRoom.capacity}). Please reduce the number of students or select a larger room.`);
      return;
    }

    const examData = {
      exam_type: examForm.exam_type,
      date: examForm.date,
      start_time: examForm.start_time,
      end_time: examForm.end_time,
      duration_minutes: parseInt(examForm.duration_minutes),
      max_students: parseInt(examForm.max_students),
      notes: examForm.notes || '',
      course: examForm.course,   // 👈 artık string (örnek: "COMP101")
      room: examForm.room        // 👈 artık string (örnek: "T312")
    };

    console.log('Sending exam data:', examData);

    if (editingExam) {
      await examAPI.updateExam(editingExam.id, examData);
    } else {
      const response = await examAPI.createExam(examData);
      console.log('Exam created successfully:', response.data);
    }

    setOpenExamDialog(false);
    fetchData();
    setError('');
  } catch (error) {
    console.error('Full error details:', error);
    let errorMessage = 'Failed to save exam';
    if (error.response?.status === 400 || error.response?.status === 500) {
      errorMessage = 'Validation error. Please check your input values.';
    }
    setError(errorMessage);
  }
};

  const getExamStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'primary';
      case 'confirmed': return 'success';
      case 'cancelled': return 'error';
      case 'completed': return 'default';
      default: return 'default';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Separate upcoming and past exams
  const now = new Date();
  const upcomingExams = exams.filter(exam => new Date(exam.date) >= now);
  const pastExams = exams.filter(exam => new Date(exam.date) < now);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <School sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            ExamFlow - Instructor Portal
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main' }}>
              {user?.first_name?.[0] || user?.username?.[0]}
            </Avatar>
            <Typography variant="body1">
              {user?.first_name} {user?.last_name}
            </Typography>
            <Button 
              color="inherit" 
              onClick={handleLogout}
              startIcon={<Logout />}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Welcome, Dr. {user?.last_name || user?.username}!
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {user?.department?.name} Department
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Event sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{upcomingExams.length}</Typography>
                    <Typography color="text.secondary">Upcoming Exams</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Schedule sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{exams.length}</Typography>
                    <Typography color="text.secondary">Total Exams</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Person sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{courses.length}</Typography>
                    <Typography color="text.secondary">My Courses</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CalendarToday sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{pastExams.length}</Typography>
                    <Typography color="text.secondary">Completed</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="My Exams" />
            <Tab label="Create Exam" />
            <Tab label="My Courses" />
          </Tabs>
        </Box>

        {/* Tab Panels */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">My Scheduled Exams</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateExam}
            >
              Create New Exam
            </Button>
          </Box>

          {loading ? (
            <Box display="flex" justifyContent="center" my={4}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {exams.map((exam) => (
                <Grid item xs={12} md={6} key={exam.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                        <Typography variant="h6">
                          {exam.course_detail?.name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip 
                            label={exam.status} 
                            color={getExamStatusColor(exam.status)}
                            size="small"
                          />
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleEditExam(exam)}>
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton size="small" onClick={() => handleDeleteExam(exam.id)}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {exam.course_detail?.code} - {exam.exam_type}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                        <CalendarToday sx={{ mr: 1, fontSize: 18 }} />
                        <Typography variant="body2">
                          {formatDate(exam.date)}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <Schedule sx={{ mr: 1, fontSize: 18 }} />
                        <Typography variant="body2">
                          {formatTime(exam.start_time)} - {formatTime(exam.end_time)}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <Room sx={{ mr: 1, fontSize: 18 }} />
                        <Typography variant="body2">
                          {exam.room_detail?.building?.code}-{exam.room_detail?.name} (Cap: {exam.room_detail?.capacity})
                        </Typography>
                      </Box>
                      
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        Students: {exam.max_students} | Duration: {exam.duration_minutes} min
                      </Typography>
                      
                      {exam.notes && (
                        <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
                          Note: {exam.notes}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h5" gutterBottom>Create New Exam</Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Use this form to schedule a new exam. The system will check for room availability and conflicts automatically.
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<Add />}
            onClick={handleCreateExam}
          >
            Create New Exam
          </Button>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h5" gutterBottom>My Courses</Typography>
          <Grid container spacing={3}>
            {courses.map((course) => (
              <Grid item xs={12} md={6} key={course.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {course.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {course.code} - {course.credits} Credits
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {course.semester}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Container>

      {/* Create/Edit Exam Dialog */}
      <Dialog open={openExamDialog} onClose={() => setOpenExamDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingExam ? 'Edit Exam' : 'Create New Exam'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Course</InputLabel>
                <Select
  name="course"
  value={examForm.course}
  onChange={handleExamFormChange}
>
  {courses.map((course) => (
    <MenuItem key={course.id} value={course.code}>
      {course.code} - {course.name}
    </MenuItem>
  ))}
</Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Exam Type</InputLabel>
                <Select
                  name="exam_type"
                  value={examForm.exam_type}
                  onChange={handleExamFormChange}
                >
                  <MenuItem value="midterm">Midterm</MenuItem>
                  <MenuItem value="final">Final</MenuItem>
                  <MenuItem value="quiz">Quiz</MenuItem>
                  <MenuItem value="makeup">Makeup</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="date"
                label="Date"
                type="date"
                value={examForm.date}
                onChange={handleExamFormChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                name="start_time"
                label="Start Time"
                type="time"
                value={examForm.start_time}
                onChange={handleExamFormChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                name="duration_minutes"
                label="Duration (minutes)"
                type="number"
                value={examForm.duration_minutes}
                onChange={handleExamFormChange}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                name="end_time"
                label="End Time"
                type="time"
                value={examForm.end_time}
                onChange={handleExamFormChange}
                InputLabelProps={{ shrink: true }}
                disabled
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Room</InputLabel>
                <Select
  name="room"
  value={examForm.room}
  onChange={handleExamFormChange}
>
  {rooms.map((room) => (
    <MenuItem key={room.id} value={room.name}>
      {room.building?.code}-{room.name} (Capacity: {room.capacity})
    </MenuItem>
  ))}
</Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="max_students"
                label="Maximum Students"
                type="number"
                value={examForm.max_students}
                onChange={handleExamFormChange}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="notes"
                label="Notes (Optional)"
                multiline
                rows={3}
                value={examForm.notes}
                onChange={handleExamFormChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenExamDialog(false)}>Cancel</Button>
          <Button onClick={handleExamSubmit} variant="contained">
            {editingExam ? 'Update Exam' : 'Create Exam'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default InstructorDashboard;