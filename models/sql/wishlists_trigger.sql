create or replace function deal_with_wishlist_changes() returns trigger as
$update_wishlists$
begin
    if (tg_op = 'DELETE') then
        -- wishlist item was deleted
        insert into "archived_wishlists" ("id", "item", "status", "purchased_by", "user_id", "event_id")
        values (old."id", old."item", old."status", old."purchased_by", old."user_id", old."event_id");
        return old;
    elsif (tg_op = 'UPDATE') then
        -- wishlist item was updated

        return new;
    elsif (tg_op = 'INSERT') then
        -- wishlist item was added

        return new;
    end if;
    return null;
end;
$update_wishlists$ language plpgsql;

drop trigger if exists wishlist_update_trigger on "wishlists";

create trigger wishlist_update_trigger
    before delete
    on "wishlists"
    for each row
execute procedure deal_with_wishlist_changes();