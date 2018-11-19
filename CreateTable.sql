-- Table: public.cameralist

-- DROP TABLE public.cameralist;

CREATE TABLE public.cameralist
(
    seq integer NOT NULL,
    device_name character varying(128) COLLATE pg_catalog."default",
    ip_addr character varying(32) COLLATE pg_catalog."default",
    rtsp_url1 character varying(128) COLLATE pg_catalog."default",
    rtsp_url2 character varying(128) COLLATE pg_catalog."default",
    status integer,
    cnterror integer,
    vms_ip character varying(64) COLLATE pg_catalog."default",
    vms_ch character varying(64) COLLATE pg_catalog."default",
    last_alive character varying(64) COLLATE pg_catalog."default",
    last_dead character varying(64) COLLATE pg_catalog."default",
    checkupdate integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.cameralist
    OWNER to postgres;

-- Table: public.cameraupdate

-- DROP TABLE public.cameraupdate;

CREATE TABLE public.cameraupdate
(
    checktime character varying(64) COLLATE pg_catalog."default",
    seq integer NOT NULL,
    device_name character varying(128) COLLATE pg_catalog."default",
    prev_ip_addr character varying(32) COLLATE pg_catalog."default",
    prev_rtsp_url1 character varying(128) COLLATE pg_catalog."default",
    prev_rtsp_url2 character varying(128) COLLATE pg_catalog."default",
    curr_ip_addr character varying(32) COLLATE pg_catalog."default",
    curr_rtsp_url1 character varying(128) COLLATE pg_catalog."default",
    curr_rtsp_url2 character varying(128) COLLATE pg_catalog."default",
    append character varying(32) COLLATE pg_catalog."default",
    prevname character varying(128) COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.cameraupdate
    OWNER to postgres;    