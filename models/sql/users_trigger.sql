create or replace function deal_with_user_changes() returns trigger as
$update_user$
declare
    user_new_email_row "emails"%ROWTYPE;
    user_old_email_row "emails"%ROWTYPE;
begin
    if (tg_op = 'DELETE') then
        -- user was deleted
        raise exception 'Not allowed due to integrity reasons';
    elsif (tg_op = 'UPDATE') then
        -- user was modified
        if (old.email != new.email) then
            select 1
            into user_old_email_row
            from "emails"
            where email = old.email;

            if found then
                if user_old_email_row."primary" then
                    update "emails" set "primary"= false where "email" = old.email;
                end if;
            else
                -- this should **not** be possible but let's store the e-mail
                -- e-mail being used by an user didn't exist...
                insert into "emails" ("email", "verified", "primary", "user_id")
                values (old."email", true, false, old."id");
            end if;

            select 1
            into user_new_email_row
            from "emails"
            where email = new.email;

            if found then
                if user_new_email_row."primary" then
                    -- already primary
                else
                    -- mark as primary
                    update "emails" set "primary"= true where "email" = new."email";
                end if;
            else
                -- new e-mail being used
                insert into "emails" ("email", "verified", "primary", "user_id")
                values (new."email", false, true, old."id");
            end if;
        end if;

        if (old.password != new.password) then
            -- mark old one inactive
            update users_passwords set "active"= false where "password" = old."password";

            -- new password should **never** exist already in the DB due to salting
            insert into users_passwords ("user_id", "password", "active") values (old."id", new."password", true);
        end if;

        if (old.confirmed_at is null and new."confirmed_at" is not null) then
            update "emails" set "verified"= true where "email" = old.email;

            insert into audit_events (event_type_id, user_id) values (2, old.id);
        end if;

        return new;
    elsif (tg_op = 'INSERT') then
        -- new user
        insert into "emails" ("email", "verified", "primary", "user_id") values (new."email", false, true, old."id");

        insert into users_passwords ("user_id", "password", "active") values (new."id", new."password", true);
        return new;
    end if;
    return null;
exception
    when others then
        insert into audit_events (event_type_id, user_id) values (1, old.id);
        return null;
end;
$update_user$ language plpgsql;

drop trigger if exists user_update_trigger on "users";

create trigger user_update_trigger
    before insert or delete or update
    on users
    for each row
execute procedure deal_with_user_changes();