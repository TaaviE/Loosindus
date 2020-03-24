-- Copyright: Taavi Eomäe 2017-2020
-- SPDX-License-Identifier: AGPL-3.0-only
create or replace function deal_with_email_changes() returns trigger as
$update_email$
declare
    email_user_row                 "users"%ROWTYPE;
    email_user_alternate_email_row "emails"%ROWTYPE;
begin
    if (tg_op = 'DELETE') then
        -- e-mail column was deleted
        -- this should only be done in settings UI email management

        -- add into audit log that an email was deleted
        insert into audit_events (event_type_id, user_id) values (10, old.user_id);

        select 1 into email_user_row from "users" where email = old.email;
        if found then
            -- to-be-deleted old e-mail exists as primary in the user's row

            -- find if there's a row that can be used instead
            select 1
            into email_user_alternate_email_row
            from "emails"
            where user_id = old.user_id
              and verified = true
              and "primary" = false;

            if found then
                -- there's an e-mail that is verified but not primary
                if not email_user_alternate_email_row."primary" then
                    update "emails" set "primary"= true where "email" = email_user_alternate_email_row.email;
                else
                    -- the new e-mail is already the primary one
                end if;

                -- set the user row primary to what we found is suitable to be used as primary
                update "users" set email=email_user_alternate_email_row.email where user_id = old.user_id;
            else
                -- we have no e-mails that are verified or not primary
                -- what will the user have as the account e-mail then?
                select 1
                into email_user_alternate_email_row
                from "emails"
                where user_id = old.user_id
                  and verified = true
                  and "primary" = true;

                if not found then
                    -- let's cancel this deletion
                    raise exception 'fallback e-mail for user % not found', old.user_id;
                else
                    -- the user already has another primary e-mail which is nice
                end if;
            end if;
        else
            -- nothing has to be updated because nothing is using the email deleted
        end if;

        -- as a last thing when it's certain the row gets deleted
        if not exists(select 1 from "deleted_emails" where email = old.email) then
            -- store a temporary backup of the email row so account recovery could be done manually if needed
            insert into deleted_emails (email, verified, "primary", user_id, added, deleted)
            values (old.email, old.verified, old.primary, old.user_id, old.added, now());
        end if;

        return old;
    elsif (tg_op = 'INSERT') then
        -- new e-mail column
        insert into audit_events (event_type_id, user_id) values (9, new.user_id);

        -- can't have two primary e-mails
        if new."primary" then
            select 1
            into email_user_alternate_email_row
            from "emails"
            where user_id = new.user_id
              and verified = true
              and "primary" = true;

            if found then
                update "emails" set "primary"= false where "email" = email_user_alternate_email_row.email;
            end if;
        end if;

        if exists(select 1 from "users" where email = new.email) then
            -- one user already uses the e-mail
            if not new.primary then
                new.primary := true;
            end if;
        else
            if new.primary then
                new.primary := false;
            end if;
            -- nothing uses the newly inserted e-mail
        end if;

        return new;
    elsif (tg_op = 'UPDATE') then
        insert into audit_events (event_type_id, user_id) values (11, new.user_id);
        return new;
    end if;
    return null;
end;
$update_email$ language plpgsql;

drop trigger if exists update_email_trigger on "emails";

create trigger update_email_trigger
    before insert or delete or update
    on emails
    for each row
execute procedure deal_with_email_changes();