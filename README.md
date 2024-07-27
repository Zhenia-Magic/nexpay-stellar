# Nexpay

## DISCLAIMER
This repository is a submission for the Stellar Startup Camp and only expose a part of the code related 
to stellar ecosystem. The full codebase is not available for public access.

## Overview

**Nexpay** is a blockchain-based application that provides a platform for businesses and workers to manage payroll and other financial transactions using cryptocurrency. This project uses Flutter for the frontend, FastAPI for the backend, and Stellar for blockchain transactions.

## Technical Stack

### Frontend

- **Flutter**: A UI toolkit for building natively compiled applications for mobile, web, and desktop from a single codebase. This project specifically uses Flutter to create a mobile application.

### Backend

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **Stellar SDK**: Used for handling blockchain transactions. Stellar is a decentralized protocol for sending and receiving money in any pair of currencies.
Authentication
- **Firebase Authentication**: Used for user authentication and securing API calls.

## Features

### For Business Users

- **Payroll Dashboard**: View and manage payroll activities.
- **Wallet Management**: View balances, make deposits, withdrawals, and transfers.
- **Employee Management**: Add and manage employees.

### For Workers
- **Salary Management**: View salary details and transaction history.
- **Wallet Management**: Manage deposits, withdrawals, and transfers.

## Technical Implementation

### Flutter Frontend

- **Pages and Navigation**: The app includes several pages such as the home page, wallet page, transfer page, and transaction details page. Navigation is handled using named routes.
- **State Management**: Uses stateful widgets and state management techniques to manage the app state.
- **UI Components**: Utilizes Flutter’s Material components for a consistent and responsive UI.
  
### FastAPI Backend

- **API Endpoints**: The backend provides several RESTful API endpoints for user authentication, fetching user details, managing transactions, and more.
- **Database**: Uses SQLAlchemy for ORM (Object-Relational Mapping) to interact with the database.
- **Stellar Integration**: Integrates Stellar SDK to handle blockchain transactions. The make_transaction function creates and submits transactions on the Stellar network.

### Firebase Authentication

- **User Authentication**: Utilizes Firebase Authentication to manage user sign-ups, logins, and secure API calls.
