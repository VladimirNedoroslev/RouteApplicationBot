create table users
(
    id           varchar(64) not null primary key,
    pin          varchar(14)  not null,
    full_name    varchar(100) not null,
    phone_number varchar(20)  not null,
    created_at timestamp   not null
);

alter table users
    owner to postgres;

