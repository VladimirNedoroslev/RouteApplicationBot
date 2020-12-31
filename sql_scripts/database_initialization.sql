create table users
(
    id           varchar(64) not null,
    chat_id      varchar(64) not null,
    primary key (id, chat_id),
    pin          varchar(14)  not null,
    full_name    varchar(100) not null,
    phone_number varchar(20)  not null,
    created_at timestamp   not null,
    lang varchar(2) not null default 'ru'
);

alter table users
    owner to postgres;

