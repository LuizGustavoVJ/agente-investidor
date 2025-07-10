-- Script de Inicialização do Banco de Dados
-- Agente Investidor - Microserviços

-- Criar databases para cada serviço
CREATE DATABASE auth_service;
CREATE DATABASE user_service;
CREATE DATABASE data_service;
CREATE DATABASE methodology_service;
CREATE DATABASE analysis_service;
CREATE DATABASE dashboard_service;
CREATE DATABASE notification_service;
CREATE DATABASE report_service;

-- Criar usuários para cada serviço
CREATE USER auth_user WITH PASSWORD 'auth_pass';
CREATE USER user_user WITH PASSWORD 'user_pass';
CREATE USER data_user WITH PASSWORD 'data_pass';
CREATE USER methodology_user WITH PASSWORD 'methodology_pass';
CREATE USER analysis_user WITH PASSWORD 'analysis_pass';
CREATE USER dashboard_user WITH PASSWORD 'dashboard_pass';
CREATE USER notification_user WITH PASSWORD 'notification_pass';
CREATE USER report_user WITH PASSWORD 'report_pass';

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE auth_service TO auth_user;
GRANT ALL PRIVILEGES ON DATABASE user_service TO user_user;
GRANT ALL PRIVILEGES ON DATABASE data_service TO data_user;
GRANT ALL PRIVILEGES ON DATABASE methodology_service TO methodology_user;
GRANT ALL PRIVILEGES ON DATABASE analysis_service TO analysis_user;
GRANT ALL PRIVILEGES ON DATABASE dashboard_service TO dashboard_user;
GRANT ALL PRIVILEGES ON DATABASE notification_service TO notification_user;
GRANT ALL PRIVILEGES ON DATABASE report_service TO report_user;

-- Extensões úteis
\c agente_investidor;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c auth_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c user_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c data_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c methodology_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c analysis_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c dashboard_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c notification_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c report_service;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

