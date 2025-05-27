// src/pages/HomePage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Typography, Button } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

const HomePage = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
        <Box sx={{ mb: 4 }}>
          <SchoolIcon sx={{ fontSize: 80, color: 'primary.main' }} />
          <Typography variant="h3" component="h1" gutterBottom>
            ExamFlow
          </Typography>
          <Typography variant="h6" color="text.secondary" paragraph>
            Streamlining University Exam Scheduling and Management
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleLoginClick}
        >
          Login
        </Button>
      </Container>
    </Box>
  );
};

export default HomePage;
