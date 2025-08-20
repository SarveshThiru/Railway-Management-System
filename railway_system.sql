-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 20, 2025 at 02:40 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `railway_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `fare_master`
--

CREATE TABLE `fare_master` (
  `fare_id` int(11) NOT NULL,
  `from_station` int(11) DEFAULT NULL,
  `to_station` int(11) DEFAULT NULL,
  `class_type` varchar(20) DEFAULT NULL,
  `fare_amount` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `fare_master`
--

INSERT INTO `fare_master` (`fare_id`, `from_station`, `to_station`, `class_type`, `fare_amount`) VALUES
(1, 1, 14, 'Sleeper', 380.00),
(2, 1, 14, 'AC', 1100.00),
(3, 1, 14, 'General', 190.00),
(4, 14, 1, 'Sleeper', 380.00),
(5, 14, 1, 'AC', 1100.00),
(6, 14, 1, 'General', 190.00),
(7, 1, 4, 'Sleeper', 550.00),
(8, 1, 4, 'AC', 1500.00),
(9, 1, 4, 'General', 250.00),
(10, 4, 1, 'Sleeper', 550.00),
(11, 4, 1, 'AC', 1500.00),
(12, 4, 1, 'General', 250.00),
(13, 5, 10, 'Sleeper', 900.00),
(14, 5, 10, 'AC', 2500.00),
(15, 5, 10, 'General', 450.00),
(16, 1, 6, 'Sleeper', 420.00),
(17, 1, 6, 'AC', 1200.00),
(18, 1, 6, 'General', 210.00),
(19, 14, 13, 'Sleeper', 850.00),
(20, 14, 13, 'AC', 2400.00),
(21, 14, 13, 'General', 420.00),
(22, 1, 7, 'Sleeper', 320.00),
(23, 1, 7, 'AC', 950.00),
(24, 1, 7, 'General', 160.00),
(25, 1, 3, 'Sleeper', 480.00),
(26, 1, 3, 'AC', 1350.00),
(27, 1, 3, 'General', 240.00),
(28, 15, 1, 'Sleeper', 270.00),
(29, 15, 1, 'AC', 600.00),
(30, 1, 15, 'Sleeper', 270.00),
(31, 1, 15, 'AC', 600.00);

-- --------------------------------------------------------

--
-- Table structure for table `stations`
--

CREATE TABLE `stations` (
  `station_id` int(11) NOT NULL,
  `station_name` varchar(50) DEFAULT NULL,
  `station_code` varchar(10) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stations`
--

INSERT INTO `stations` (`station_id`, `station_name`, `station_code`, `city`, `state`) VALUES
(1, 'Niligris', 'UDM', 'Metupalayam', 'Tamil Nadu'),
(2, 'Bengaluru City', 'SBC', 'Bengaluru', 'Karnataka'),
(3, 'Coimbatore Junction', 'CBE', 'Coimbatore', 'Tamil Nadu'),
(4, 'Hyderabad Deccan', 'HYB', 'Hyderabad', 'Telangana'),
(5, 'Mumbai CST', 'CSMT', 'Mumbai', 'Maharashtra'),
(6, 'Madurai Junction', 'MDU', 'Madurai', 'Tamil Nadu'),
(7, 'Tiruchchirappalli Junction', 'TPJ', 'Tiruchchirappalli', 'Tamil Nadu'),
(8, 'Salem Junction', 'SA', 'Salem', 'Tamil Nadu'),
(9, 'Erode Junction', 'ED', 'Erode', 'Tamil Nadu'),
(10, 'Visakhapatnam', 'VSKP', 'Visakhapatnam', 'Andhra Pradesh'),
(11, 'Vijayawada Junction', 'BZA', 'Vijayawada', 'Andhra Pradesh'),
(12, 'Pune Junction', 'PUNE', 'Pune', 'Maharashtra'),
(13, 'Nagpur Junction', 'NGP', 'Nagpur', 'Maharashtra'),
(14, 'KSR Bengaluru', 'SBC', 'Bengaluru', 'Karnataka'),
(15, 'Chennai Central', 'MGR', 'Chennai', 'Tamil Nadu');

-- --------------------------------------------------------

--
-- Table structure for table `tickets`
--

CREATE TABLE `tickets` (
  `ticket_id` int(11) NOT NULL,
  `pnr` varchar(20) DEFAULT NULL,
  `train_id` int(11) DEFAULT NULL,
  `passenger_id` int(11) DEFAULT NULL,
  `from_station` int(11) DEFAULT NULL,
  `to_station` int(11) DEFAULT NULL,
  `seat_number` varchar(10) DEFAULT NULL,
  `class_type` varchar(20) DEFAULT NULL,
  `booking_date` date DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `passenger_name` varchar(255) NOT NULL,
  `passenger_age` int(11) DEFAULT NULL,
  `passenger_gender` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tickets`
--

INSERT INTO `tickets` (`ticket_id`, `pnr`, `train_id`, `passenger_id`, `from_station`, `to_station`, `seat_number`, `class_type`, `booking_date`, `status`, `passenger_name`, `passenger_age`, `passenger_gender`) VALUES
(1, 'A1B2C3D4', 101, 2, 1, 14, 'S5-32', 'Sleeper', '2025-08-20', 'Confirmed', 'Rajesh Kumar', 35, 'Male'),
(2, 'E5F6G7H8', 101, 3, 1, 14, 'A1-15', 'AC', '2025-08-21', 'Confirmed', 'Sunita Mishra', 28, 'Female'),
(3, 'I9J1K2L3', 102, 5, 14, 1, 'S2-11', 'Sleeper', '2025-08-22', 'Confirmed', 'Deepak Patel', 42, 'Male'),
(4, 'M4N5O6P7', 103, 6, 1, 4, 'B2-04', 'AC', '2025-08-23', 'Cancelled', 'Lakshmi Gopal', 55, 'Female'),
(5, 'Q8R9S1T2', 103, 7, 1, 4, 'S10-72', 'Sleeper', '2025-08-24', 'Confirmed', 'Mohan Singh', 30, 'Male'),
(6, 'U3V4W5X6', 104, 8, 5, 10, 'S1-01', 'Sleeper', '2025-08-25', 'Confirmed', 'Geetha Varma', 48, 'Female'),
(7, 'Y7Z8A9B1', 105, 9, 1, 6, 'C1-18', 'AC', '2025-08-26', 'Confirmed', 'Suresh Reddy', 29, 'Male'),
(8, 'C2D3E4F5', 106, 10, 14, 13, 'S8-44', 'Sleeper', '2025-08-27', 'Confirmed', 'Anand Bhat', 38, 'Male'),
(9, 'G6H7I8J9', 101, 2, 1, 14, 'S5-33', 'Sleeper', '2025-08-28', 'Confirmed', 'Priya Kumar', 33, 'Female'),
(10, 'K1L2M3N4', 103, 5, 1, 11, 'G5-12', 'General', '2025-08-29', 'Confirmed', 'Ravi Prasad', 45, 'Male'),
(11, 'O5P6Q7R8', 105, 3, 1, 7, 'S3-08', 'Sleeper', '2025-08-30', 'Cancelled', 'Meena Kumari', 26, 'Female'),
(12, 'S9T1U2V3', 104, 6, 12, 10, 'A2-22', 'AC', '2025-08-31', 'Confirmed', 'Kiran Gopal', 58, 'Male'),
(13, 'W4X5Y6Z7', 102, 7, 14, 1, 'D4-50', 'General', '2025-09-01', 'Confirmed', 'Sita Singh', 29, 'Female'),
(14, 'A8B9C1D2', 106, 8, 1, 11, 'S6-19', 'Sleeper', '2025-09-02', 'Confirmed', 'Arjun Varma', 50, 'Male'),
(15, 'E3F4G5H6', 101, 9, 1, 14, 'S5-34', 'Sleeper', '2025-09-03', 'Confirmed', 'Vijay Reddy', 31, 'Male'),
(16, 'I7J8K9L1', 103, 10, 11, 4, 'B3-11', 'AC', '2025-09-04', 'Confirmed', 'Nisha Bhat', 36, 'Female'),
(17, 'M2N3O4P5', 105, 2, 1, 6, 'C1-19', 'AC', '2025-09-05', 'Confirmed', 'Kavitha Kumar', 34, 'Female'),
(18, 'Q6R7S8T9', 104, 5, 5, 12, 'S12-02', 'Sleeper', '2025-09-06', 'Confirmed', 'Amit Patel', 44, 'Male'),
(19, 'U1V2W3X4', 102, 3, 14, 1, 'S2-12', 'Sleeper', '2025-09-07', 'Cancelled', 'Rani Mishra', 27, 'Female'),
(20, 'Y5Z6A7B8', 106, 6, 14, 1, 'A3-01', 'AC', '2025-09-08', 'Confirmed', 'Gopal Krishna', 60, 'Male'),
(21, '2Q1PJ4LU', 103, 2, 1, 4, 'S1-1', 'AC', '2025-08-20', 'Confirmed', 'Rajesh J', 27, 'Male'),
(22, '3NACVB6K', 107, 1, 1, 15, 'S1-1', 'AC', '2025-08-20', 'Confirmed', 'Prem', 23, 'Male'),
(23, 'BML00N5I', 107, 1, 1, 15, 'S1-2', 'AC', '2025-08-20', 'Cancelled', 'Ram', 30, 'Male'),
(24, 'ASULLYX4', 107, 1, 1, 15, 'S1-2', 'AC', '2025-08-20', 'Confirmed', 'Kumar', 19, 'Male');

-- --------------------------------------------------------

--
-- Table structure for table `trains`
--

CREATE TABLE `trains` (
  `train_id` int(11) NOT NULL,
  `train_name` varchar(50) DEFAULT NULL,
  `train_type` varchar(20) DEFAULT NULL,
  `total_seats` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `trains`
--

INSERT INTO `trains` (`train_id`, `train_name`, `train_type`, `total_seats`) VALUES
(101, 'Brindavan Express', 'Superfast', 450),
(102, 'Lalbagh Express', 'Superfast', 450),
(103, 'Charminar Express', 'Express', 500),
(104, 'Konark Express', 'Superfast', 550),
(105, 'Vaigai Superfast Express', 'Superfast', 400),
(106, 'Sanghamitra Express', 'Superfast', 600),
(107, 'Niligris Exp', 'Express', 200);

-- --------------------------------------------------------

--
-- Table structure for table `train_schedule`
--

CREATE TABLE `train_schedule` (
  `schedule_id` int(11) NOT NULL,
  `train_id` int(11) DEFAULT NULL,
  `station_id` int(11) DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `sequence` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `train_schedule`
--

INSERT INTO `train_schedule` (`schedule_id`, `train_id`, `station_id`, `arrival_time`, `departure_time`, `sequence`) VALUES
(1, 101, 1, NULL, '07:50:00', 1),
(2, 101, 14, '13:40:00', NULL, 2),
(3, 102, 14, NULL, '06:30:00', 1),
(4, 102, 1, '12:20:00', NULL, 2),
(5, 103, 1, NULL, '18:10:00', 1),
(6, 103, 11, '00:10:00', '00:20:00', 2),
(7, 103, 4, '08:00:00', NULL, 3),
(8, 104, 5, NULL, '15:10:00', 1),
(9, 104, 12, '19:00:00', '19:05:00', 2),
(10, 104, 4, '03:40:00', '03:50:00', 3),
(11, 104, 11, '09:15:00', '09:25:00', 4),
(12, 104, 10, '15:20:00', NULL, 5),
(13, 105, 1, NULL, '13:50:00', 1),
(14, 105, 7, '17:40:00', '17:45:00', 2),
(15, 105, 6, '20:15:00', NULL, 3),
(16, 106, 14, NULL, '09:00:00', 1),
(17, 106, 1, '14:20:00', '14:40:00', 2),
(18, 106, 11, '21:00:00', '21:10:00', 3),
(19, 106, 13, '08:40:00', NULL, 4),
(20, 107, 1, NULL, '21:00:00', 1),
(21, 107, 15, '06:00:00', '21:00:00', 7);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `role`, `email`, `phone`) VALUES
(1, 'admin', 'adminpass', 'admin', 'admin@railway.com', '9876543210'),
(2, 'rajesh', 'rajesh123', 'user', 'rajesh.k@email.com', '9123456789'),
(3, 'sunita', 'sunita123', 'user', 'sunita.m@email.com', '9988776655'),
(4, 'travelagent', 'agentpass', 'agent', 'contact@besttravels.com', '9765432109'),
(5, 'deepak', 'deepak123', 'user', 'deepak.p@email.com', '9876511111'),
(6, 'lakshmi', 'lakshmi123', 'user', 'lakshmi.g@email.com', '9876522222'),
(7, 'mohan', 'mohan123', 'user', 'mohan.s@email.com', '9876533333'),
(8, 'geetha', 'geetha123', 'user', 'geetha.v@email.com', '9876544444'),
(9, 'suresh', 'suresh123', 'user', 'suresh.r@email.com', '9876555555'),
(10, 'anand', 'anand123', 'user', 'anand.b@email.com', '9876566666');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `fare_master`
--
ALTER TABLE `fare_master`
  ADD PRIMARY KEY (`fare_id`),
  ADD KEY `idx_fare_master_from_station` (`from_station`),
  ADD KEY `idx_fare_master_to_station` (`to_station`);

--
-- Indexes for table `stations`
--
ALTER TABLE `stations`
  ADD PRIMARY KEY (`station_id`);

--
-- Indexes for table `tickets`
--
ALTER TABLE `tickets`
  ADD PRIMARY KEY (`ticket_id`),
  ADD UNIQUE KEY `pnr` (`pnr`),
  ADD KEY `idx_tickets_train_id` (`train_id`),
  ADD KEY `idx_tickets_passenger_id` (`passenger_id`),
  ADD KEY `idx_tickets_from_station` (`from_station`),
  ADD KEY `idx_tickets_to_station` (`to_station`);

--
-- Indexes for table `trains`
--
ALTER TABLE `trains`
  ADD PRIMARY KEY (`train_id`);

--
-- Indexes for table `train_schedule`
--
ALTER TABLE `train_schedule`
  ADD PRIMARY KEY (`schedule_id`),
  ADD KEY `station_id` (`station_id`),
  ADD KEY `idx_train_schedule_train_id` (`train_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `fare_master`
--
ALTER TABLE `fare_master`
  MODIFY `fare_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `stations`
--
ALTER TABLE `stations`
  MODIFY `station_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tickets`
--
ALTER TABLE `tickets`
  MODIFY `ticket_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `trains`
--
ALTER TABLE `trains`
  MODIFY `train_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;

--
-- AUTO_INCREMENT for table `train_schedule`
--
ALTER TABLE `train_schedule`
  MODIFY `schedule_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `fare_master`
--
ALTER TABLE `fare_master`
  ADD CONSTRAINT `fare_master_ibfk_1` FOREIGN KEY (`from_station`) REFERENCES `stations` (`station_id`),
  ADD CONSTRAINT `fare_master_ibfk_2` FOREIGN KEY (`to_station`) REFERENCES `stations` (`station_id`);

--
-- Constraints for table `tickets`
--
ALTER TABLE `tickets`
  ADD CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`train_id`) REFERENCES `trains` (`train_id`),
  ADD CONSTRAINT `tickets_ibfk_2` FOREIGN KEY (`passenger_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `tickets_ibfk_3` FOREIGN KEY (`from_station`) REFERENCES `stations` (`station_id`),
  ADD CONSTRAINT `tickets_ibfk_4` FOREIGN KEY (`to_station`) REFERENCES `stations` (`station_id`);

--
-- Constraints for table `train_schedule`
--
ALTER TABLE `train_schedule`
  ADD CONSTRAINT `train_schedule_ibfk_1` FOREIGN KEY (`train_id`) REFERENCES `trains` (`train_id`),
  ADD CONSTRAINT `train_schedule_ibfk_2` FOREIGN KEY (`station_id`) REFERENCES `stations` (`station_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
