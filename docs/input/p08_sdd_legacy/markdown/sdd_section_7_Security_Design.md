# 7 Security Design

## Introduction
This section documents the actual security design of the Legacy Banking System, focusing on access control and data protection mechanisms. It covers the implemented security measures, including authentication, authorization, and data encryption strategies. The section is divided into two main subsections: Access Control Design and Data Protection Design.

## 7.1 Access Control Design
This subsection details the access control mechanisms implemented in the Legacy Banking System, focusing on authentication and authorization processes.

### LegacyAuthService.java
- **Purpose**: Implements core user authentication and authorization logic, including session management and role-based access control.
- **Source Files**: `/src/main/java/com/example/legacy/auth/LegacyAuthService.java`
- **Key Features**:
  - User authentication with username and password
  - Role-based access control
  - Session management with expiration
- **Interfaces**:
  - `authenticateUser(username, password)`
  - `authorizeAction(userId, permission)`
  - `createSession(userId)`
  - `validateSession(sessionId)`

### AccessControlPolicyEngine.php
- **Purpose**: Defines and enforces access control policies across the application.
- **Source Files**: `/app/core/security/AccessControlPolicyEngine.php`
- **Key Features**:
  - Dynamic policy evaluation
  - Role and permission management
  - Complex conditional logic for access decisions
- **Interfaces**:
  - `canAccess(user, resource, action)`

## 7.2 Data Protection Design
This subsection describes the data protection strategies, focusing on encryption methods used to secure sensitive information.

### DataProtectionUtil.cs
- **Purpose**: Provides utility methods for encrypting and decrypting sensitive data.
- **Source Files**: `/Utils/Security/DataProtectionUtil.cs`
- **Key Features**:
  - Data encryption and decryption
  - Hardcoded encryption key
  - Symmetric encryption algorithm
- **Interfaces**:
  - `Encrypt(string data)`
  - `Decrypt(string encryptedData)`

## Summary
- **Key Decisions**:
  - Use of role-based access control for managing user permissions.
  - Implementation of custom encryption methods for data protection.
- **Trade-offs**:
  - Custom encryption methods may pose security risks due to outdated algorithms.
  - Monolithic access control logic can lead to performance bottlenecks.
- **Future Considerations**:
  - Consider upgrading encryption algorithms to modern standards.
  - Refactor access control logic to improve scalability and maintainability.

## Implementation
- **Development Guidance**:
  - Ensure encryption keys are securely managed and rotated regularly.
  - Implement logging for authentication and authorization events for audit purposes.
  - Avoid hardcoding sensitive information within the codebase.
- **Testing Approach**: Conduct penetration testing to identify security vulnerabilities and validate access control policies.
- **Deployment Notes**: Ensure secure configuration of servers and databases to prevent unauthorized access.

## Modernization
- **Current Technology**: The system uses a COBOL and CICS environment with custom Java, PHP, and C# components.
- **Modernization Options**:
  - Migrate to a microservices architecture for better scalability.
  - Adopt modern encryption standards like AES for data protection.
- **Refactoring Opportunities**:
  - Decouple access control logic to improve flexibility.
  - Implement centralized key management for encryption operations.