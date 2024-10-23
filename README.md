# Django Booking Service

A comprehensive customer relationship management (CRM) application built with Django, designed for managing bookings and reviews effectively.

## Features

- **User Registration and Authentication**: 
  - Users can register as regular users or masters (service providers).
  - Secure login/logout functionality.

- **User and Master Profiles**: 
  - Users can manage their profiles, including personal information and preferences.
  - Masters can showcase their skills and experience.

- **Order Management**: 
  - Users can create, update, and delete their bookings.
  - Masters can view and accept available orders.
  - Order statuses include Pending, Confirmed, In Progress, Completed, and Canceled.

- **Review System**: 
  - Users can leave reviews and ratings for completed orders.
  - Masters can view feedback from users to improve their services.

- **Notifications**: 
  - Users receive notifications for order updates, payment reminders, and new reviews.
  - Masters receive notifications for new orders and reviews.

- **Search and Filter**: 
  - Users can search for masters based on categories, experience, and location.
  - Advanced filtering options for viewing orders based on various criteria.

- **Payment Integration**: 
  - Secure payment processing through Stripe.
  - Users can make payments for orders directly through the application.

- **Responsive Design**: 
  - Built with Bootstrap for a user-friendly interface on all devices.

## Technologies Used

- Python 3.x
- Django 5.x
- MySQL/PostgreSQL for database management
- Nginx for serving static files and reverse proxy
- HTML/CSS for front-end design
- Bootstrap for responsive design
- Stripe for payment processing

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kostya99912/HousePro
   cd HousePro