// src/pages/StudentDashboard.js
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
  Avatar
} from '@mui/material';
import {
  School,
  Event,
  Schedule,
  Person,
  Logout,
  CalendarToday,
  Room
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { examAPI } from '../services/api';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    try {
      const response = await examAPI.getExams({
        department: user.department?.id
      });
      setExams(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error fetching exams:', error);
      setError('Failed to load exams');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
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
            ExamFlow - Student Portal
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
            Welcome, {user?.first_name || user?.username}!
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {user?.department?.name} - {user?.student_id}
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
                    <Typography variant="h4">{user?.department?.code}</Typography>
                    <Typography color="text.secondary">Department</Typography>
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

        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Upcoming Exams */}
            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
              Upcoming Exams
            </Typography>
            {upcomingExams.length === 0 ? (
              <Alert severity="info">No upcoming exams scheduled.</Alert>
            ) : (
              <Grid container spacing={3}>
                {upcomingExams.map((exam) => (
                  <Grid item xs={12} md={6} key={exam.id}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Typography variant="h6">
                            {exam.course?.name}
                          </Typography>
                          <Chip 
                            label={exam.status} 
                            color={getExamStatusColor(exam.status)}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {exam.course?.code} - {exam.exam_type}
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
                            {exam.room?.building?.code}-{exam.room?.name}
                          </Typography>
                        </Box>
                        
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

            {/* Past Exams */}
            {pastExams.length > 0 && (
              <>
                <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
                  Past Exams
                </Typography>
                <Grid container spacing={3}>
                  {pastExams.slice(0, 4).map((exam) => (
                    <Grid item xs={12} md={6} key={exam.id}>
                      <Card sx={{ opacity: 0.7 }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="h6">
                              {exam.course?.name}
                            </Typography>
                            <Chip 
                              label="Completed" 
                              color="default"
                              size="small"
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {exam.course?.code} - {formatDate(exam.date)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </>
            )}
          </>
        )}
      </Container>
    </>
  );
};

export default StudentDashboard;