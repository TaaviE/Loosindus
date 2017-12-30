CREATE TABLE wishlist
(
  user_id         SERIAL NOT NULL
    CONSTRAINT wishlist_user_id_pk
    PRIMARY KEY,
  notes           JSON,
  notes_purchased JSON
);

CREATE TABLE role
(
  id          SERIAL NOT NULL
    CONSTRAINT role_pkey
    PRIMARY KEY,
  name        VARCHAR(80),
  description VARCHAR(255)
);

CREATE UNIQUE INDEX role_id_uindex
  ON role (id);

CREATE UNIQUE INDEX role_name_uindex
  ON role (name);

CREATE TABLE "user"
(
  id           SERIAL NOT NULL
    CONSTRAINT user_id_pk
    PRIMARY KEY,
  email        VARCHAR(255),
  password     VARCHAR(255),
  confirmed_at TIMESTAMP,
  active       BOOLEAN,
  username     VARCHAR(255),
  family_id    INTEGER
);

CREATE UNIQUE INDEX user_id_uindex
  ON "user" (id);

CREATE UNIQUE INDEX user_email_uindex
  ON "user" (email);

CREATE UNIQUE INDEX user_username_uindex
  ON "user" (username);

ALTER TABLE wishlist
  ADD CONSTRAINT wishlist_user_id_fkey
FOREIGN KEY (user_id) REFERENCES "user";

CREATE TABLE roles_users
(
  id      INTEGER
    CONSTRAINT roles_users_id_fkey
    REFERENCES "user",
  role_id INTEGER
    CONSTRAINT roles_users_role_id_fkey
    REFERENCES role
);

CREATE TABLE families
(
  id      SERIAL  NOT NULL
    CONSTRAINT families_pkey
    PRIMARY KEY,
  name    VARCHAR(255),
  "group" INTEGER NOT NULL
);

CREATE UNIQUE INDEX families_id_uindex
  ON families (id);

ALTER TABLE "user"
  ADD CONSTRAINT user_family_id_fkey
FOREIGN KEY (family_id) REFERENCES families;

CREATE TABLE shuffles
(
  giver  INTEGER NOT NULL
    CONSTRAINT shuffles_pkey
    PRIMARY KEY
    CONSTRAINT shuffles_giver_fkey
    REFERENCES "user",
  getter INTEGER NOT NULL
    CONSTRAINT shuffles_getter_fkey
    REFERENCES "user"
);

CREATE UNIQUE INDEX shuffles_giver_uindex
  ON shuffles (giver);

CREATE UNIQUE INDEX shuffles_getter_uindex
  ON shuffles (getter);

CREATE TABLE groups
(
  id          SERIAL  NOT NULL
    CONSTRAINT groups_pkey
    PRIMARY KEY,
  admin       INTEGER NOT NULL
    CONSTRAINT groups_admin_fkey
    REFERENCES "user",
  description VARCHAR(255)
);

CREATE UNIQUE INDEX groups_id_uindex
  ON groups (id);

ALTER TABLE families
  ADD CONSTRAINT families_group_fkey
FOREIGN KEY ("group") REFERENCES groups;

