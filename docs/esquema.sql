CREATE TABLE pacientes (
	id SERIAL NOT NULL, 
	documento VARCHAR(20) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	telefono VARCHAR(20) NOT NULL, 
	fecha_nacimiento TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (documento)
);

CREATE TABLE roles (
	id SERIAL NOT NULL, 
	nombre VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE TABLE sedes (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	vereda VARCHAR(100) NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE TABLE servicios (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	duracion_media_min INTEGER NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);

CREATE TABLE profesionales (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	sede_id INTEGER NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sede_id) REFERENCES sedes (id)
);

CREATE TABLE usuarios (
	id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	correo VARCHAR(120) NOT NULL, 
	clave_hash VARCHAR(200) NOT NULL, 
	rol_id INTEGER NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	creado_en TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (correo), 
	FOREIGN KEY(rol_id) REFERENCES roles (id)
);

CREATE TABLE auditoria (
	id SERIAL NOT NULL, 
	usuario_id INTEGER, 
	entidad VARCHAR(40) NOT NULL, 
	registro_id INTEGER NOT NULL, 
	accion VARCHAR(20) NOT NULL, 
	detalle TEXT NOT NULL, 
	fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

CREATE INDEX ix_auditoria_entidad ON auditoria (entidad);

CREATE TABLE citas (
	id SERIAL NOT NULL, 
	paciente_id INTEGER NOT NULL, 
	profesional_id INTEGER NOT NULL, 
	servicio_id INTEGER NOT NULL, 
	sede_id INTEGER NOT NULL, 
	llegada TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	inicio_atencion TIMESTAMP WITHOUT TIME ZONE, 
	fin_atencion TIMESTAMP WITHOUT TIME ZONE, 
	estado VARCHAR(20) NOT NULL, 
	prioridad VARCHAR(20) NOT NULL, 
	eliminado BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(paciente_id) REFERENCES pacientes (id), 
	FOREIGN KEY(profesional_id) REFERENCES profesionales (id), 
	FOREIGN KEY(servicio_id) REFERENCES servicios (id), 
	FOREIGN KEY(sede_id) REFERENCES sedes (id)
);

CREATE INDEX ix_citas_llegada ON citas (llegada);

CREATE TABLE profesional_servicio (
	profesional_id INTEGER NOT NULL, 
	servicio_id INTEGER NOT NULL, 
	PRIMARY KEY (profesional_id, servicio_id), 
	FOREIGN KEY(profesional_id) REFERENCES profesionales (id), 
	FOREIGN KEY(servicio_id) REFERENCES servicios (id)
);
