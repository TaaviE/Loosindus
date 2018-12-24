create table groups
(
	id serial not null
		constraint groups_pkey
			primary key,
	name varchar(255),
	description integer
);

create table families
(
	id serial not null
		constraint families_pkey
			primary key,
	name varchar(255),
	"group" integer not null
		constraint families_group_fkey
			references groups,
	creation timestamp default now() not null
);

create unique index families_id_uindex
	on families (id);

create unique index groups_id_uindex
	on groups (id);

create table names_genitive
(
	name varchar(255) not null
		constraint names_genitive_pkey
			primary key,
	genitive varchar(255) not null
);

create unique index names_genitive_name_uindex
	on names_genitive (name);

create table role
(
	id serial not null
		constraint role_pkey
			primary key,
	name varchar(80),
	description varchar(255)
);

create unique index role_id_uindex
	on role (id);

create unique index role_name_uindex
	on role (name);

create table "user"
(
	id serial not null
		constraint user_id_pk
			primary key,
	email varchar(255),
	password varchar(255),
	confirmed_at timestamp,
	active boolean,
	username varchar(255),
	last_login_at timestamp,
	current_login_at timestamp,
	last_login_ip varchar(255),
	current_login_ip varchar(255),
	login_count integer,
	last_activity_at timestamp,
	last_activity_ip varchar(255),
	language varchar(5) default 'en'::character varying not null,
	first_seen timestamp default now() not null
);

create table roles_users
(
	id integer
		constraint roles_users_id_fkey
			references "user",
	role_id integer
		constraint roles_users_role_id_fkey
			references role
);

create table shuffles
(
	giver integer not null
		constraint shuffles_pkey
			primary key
		constraint shuffles_giver_fkey
			references "user",
	getter integer not null
		constraint shuffles_getter_fkey
			references "user",
	year timestamp not null,
	"group" integer not null
		constraint shuffles_groups_id_fk
			references groups
);

create index shuffles_group_index
	on shuffles ("group");

create index shuffles_group_giver_index
	on shuffles ("group", giver);

create unique index shuffles_giver_group_getter_year_uindex
	on shuffles (giver, "group", getter, year);

create unique index user_email_uindex
	on "user" (email);

create unique index user_id_uindex
	on "user" (id);

create index user_username_index
	on "user" (username);

create table users_families_admins
(
	user_id integer not null
		constraint users_families_admins_pkey
			primary key
		constraint users_families_admins_user_id_fkey
			references "user",
	family_id integer not null
		constraint users_families_admins_family_id_fkey
			references families,
	admin boolean not null
);

comment on table users_families_admins is 'Contains all user-family relationships and if the user is the admin of that family';

create table users_groups_admins
(
	user_id integer not null
		constraint users_groups_admins_user_id_pk
			primary key
		constraint users_groups_admins_user_id_fkey
			references "user",
	group_id integer not null
		constraint users_groups_admins_group_id_fkey
			references groups,
	admin boolean not null
);

create table wishlists
(
	user_id integer not null
		constraint wishlists_user_id_fkey
			references "user",
	item varchar(1024) not null,
	status integer not null,
	purchased_by integer
		constraint wishlists_purchased_by_fkey
			references "user",
	id bigserial not null
		constraint wishlists_note_id_pk
			primary key
);

create unique index wishlists_note_id_uindex
	on wishlists (id);

create table families_groups
(
	family_id integer not null
		constraint families_groups_admins_pk
			primary key
		constraint families_groups_admins_families_id_fk
			references families,
	group_id integer not null
		constraint families_groups_admins_groups_id_fk
			references groups
);

create index families_groups_admins_family_id_index
	on families_groups (family_id);

create index families_groups_admins_group_id_index
	on families_groups (group_id);

create table user_connection
(
	id serial not null
		constraint user_connection_pk
			primary key,
	user_id integer not null
		constraint user_connection_user_id_fk
			references "user",
	provider_user_id varchar(255),
	created_at timestamp default now(),
	token varchar(255),
	provider varchar(255)
);

create unique index user_connection_id_uindex
	on user_connection (id);

create table reminders
(
	"group" integer not null
		constraint reminders_pk
			primary key
		constraint reminders_groups_id_fk
			references groups,
	last_check timestamp default now() not null,
	type varchar(4)
);

create index reminders_group_index
	on reminders ("group");

