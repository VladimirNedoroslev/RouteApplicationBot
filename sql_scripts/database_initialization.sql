create table user_chats
(
    id         varchar(64) not null PRIMARY KEY,
    chat_id    varchar(64) not null UNIQUE,
    created_at timestamp   not null
);

create table users
(
    id           varchar(64) references user_chats (id) primary key,
    pin          varchar(14)  not null,
    full_name    varchar(100) not null,
    phone_number varchar(20)  not null
);

alter table user_chats
    owner to postgres;

alter table users
    owner to postgres;

