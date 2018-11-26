-- Django's migration tool didn't seem to apply my foreign keys, all the indexes and used wrong column types

create table shuffles
(
	giver integer not null
		constraint "SecretSanta_shuffle_pkey"
			primary key
		constraint shuffles_auth_user_id_fk
			references auth_user,
	getter integer not null
		constraint shuffles_auth_user_id_fk_2
			references auth_user,
	year date not null
);

alter table shuffles owner to jolod;

create index shuffles_getter_index
	on shuffles (getter);

create table wishlists
(
	id integer not null
		constraint "SecretSanta_wishlist_pkey"
			primary key,
	user_id integer not null
		constraint wishlists_auth_user_id_fk
			references auth_user,
	item varchar(1024) not null,
	status integer not null,
	purchased_by integer
		constraint wishlists_auth_user_id_fk_2
			references auth_user
);

alter table wishlists owner to jolod;

create index wishlists_user_id_index
	on wishlists (user_id);

create index wishlists_purchased_by_index
	on wishlists (purchased_by);

create table groups
(
	id integer not null
		constraint groups_pkey
			primary key,
	description varchar(255),
	year date not null
);

alter table groups owner to jolod;

create table families
(
	group_id integer not null
		constraint families_groups_id_fk
			references groups,
	name varchar(255) not null,
	id integer not null
		constraint families_pk
			primary key
);

alter table families owner to jolod;

create unique index families_id_uindex
	on families (id);

create index families_group_id_index
	on families (group_id);

create table familyadmins
(
	family_id integer not null
		constraint familyadmins_families_id_fk
			references families,
	admin boolean not null,
	user_id integer not null
		constraint familyadmins_pk
			primary key
		constraint familyadmins_auth_user_id_fk
			references auth_user
);

alter table familyadmins owner to jolod;

create index familyadmins_user_id_index
	on familyadmins (user_id);

create index familyadmins_family_id_index
	on familyadmins (family_id);

create table groupadmins
(
	user_id integer not null
		constraint groupadmins_pkey
			primary key
		constraint groupadmins_auth_user_id_fk
			references auth_user,
	group_id integer not null
		constraint groupadmins_groups_id_fk
			references groups,
	admin boolean not null
);

alter table groupadmins owner to jolod;

create index groupadmins_group_id_index
	on groupadmins (group_id);

create table names_genitive
(
	name varchar(255) not null
		constraint names_genitive_pkey
			primary key,
	genitive varchar(255) not null
);

alter table names_genitive owner to jolod;

create index names_genitive_name_b652d0f6_like
	on names_genitive (name);

