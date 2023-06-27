drop database gatemanagement;
create database gatemanagement;
use gatemanagement;

-- creating tables 
create table users(
	UID int unsigned not null auto_increment,
    Name varchar(30) not null,
    Password varchar(30) not null,
    SecurityQuestion enum('Nickname','Favourite Book', 'Hobby' ) not null,
    Answer varchar(30) not null,
    AddressLines varchar(200) not null,
    Pincode int unsigned not null,
    primary key (UID)
);

create table vehicles(
  VehicleNo varchar(15) not null,
  Owner int unsigned not null,
  Type enum ('car', 'bike', 'scooty') not null,
  foreign key (Owner) references users(UID),
  primary key (vehicleNo)
  );
    
create table userEntries(
  UserEntryID int unsigned not null auto_increment,
  UID int unsigned not null,
  EntryTime datetime default current_timestamp on update current_timestamp not null,
  Primary key (userEntryID),
  foreign key (UID) references users(UID)
  );


create table vehicleEntries(
  vehicleEntryID int unsigned not null auto_increment,
  userEntryID int unsigned not null,
  vehicleNo varchar(15) not null,
  primary key(vehicleEntryID),
  foreign key (userentryid) references userentries(userentryid),
  foreign key (vehicleno) references vehicles(vehicleno)
  );


create table userExits(
  userExitID int unsigned not null auto_increment,
  userEntryID int unsigned not null,
  exitTime datetime default current_timestamp on update current_timestamp not null,
  primary key(userExitID),
  foreign key (userEntryId) references userEntries(userEntryId)
  );
  

create table vehicleExits(
  vehicleExitId int unsigned not null auto_increment,
  userExitId int unsigned not null,
  vehicleEntryId int unsigned not null,
  exitTime datetime default current_timestamp on update current_timestamp not null,
  primary key(vehicleExitID),
  foreign key (userExitId) references userExits(userExitId),
  foreign key (vehicleEntryId) references vehicleEntries(vehicleEntryId) 
  );
  
  show tables;
  
  insert into users values 
	(1,"Mehak", "mehak02", "Favourite Book","singhee" ,"BITS Pilani, Pilani Campus" , 333031 ),
    (2,"Ayush", "aygupta", "Nickname", "gupta","BITS Pilani, Pilani Campus", 333031),
	(3,"Suraj", "phalod", "Hobby", "robotics","BITS Pilani, Pilani Campus", 333031),
	(4,"Raashi", "vanwaani", "Hobby", "poetry","BITS Pilani, Pilani Campus", 333031),
	(5,"Rahul", "ginodia", "Hobby", "blockchain","BITS Pilani, Goa Campus", 333031),
	(6,"Kartik", "dang", "Hobby", "photog","BITS Pilani, Goa Campus", 333031),
	(7,"Gautam", "france", "Nickname", "jajoo","BITS Pilani, Goa Campus", 333031),
	(8,"Bhavishya", "garg", "Favourite Book", "harrypotter","BITS Pilani, Goa Campus", 333031),
	(9,"Karan", "competitive", "Favourite Book", "alchemist","BITS Pilani, Pilani Campus", 333031),
    (10,"Karan", "coding", "Nickname", "ptanhi","BITS Pilani, Pilani Campus", 333031);
    
select * from users;
insert into vehicles values
	('WB08AB4200', 1, 'car'),
    ('RJABCD1234', 2, 'bike'),
    ('UP1G2B8421', 4, 'scooty'),
    ('UP15BF1425', 9, 'bike'),
    ('MP18BF1485', 10, 'car'),
    ('GJ14JG7894', 6, 'bike'),
    ('GA45UI7894', 4, 'car');
 

-- procedure to update the password
DELIMITER $$
CREATE PROCEDURE updatePassword( 
IN new_password varchar(25) , IN given_answer varchar(32) , IN given_uid int unsigned)
BEGIN
set @answer = (select answer from users where uid=given_uid);
if @answer = given_answer then 
UPDATE users
SET password = new_password
WHERE uid =given_uid ;
end if ;
END$$
DELIMITER ;

-- procedure to update the address
DELIMITER $$
CREATE PROCEDURE updateAddress( 
IN new_address varchar(25) , IN given_answer varchar(32) , IN given_uid int unsigned)
BEGIN
set @answer = (select answer from users where uid=given_uid);
if @answer = given_answer then 
UPDATE users
SET addresslines = new_address
WHERE uid =given_uid ;
end if ;
END$$
DELIMITER ;
 
-- procedure to update the pincode
DELIMITER $$
CREATE PROCEDURE updatePincode( 
IN new_pincode varchar(25) , IN given_answer varchar(32) , IN given_uid int unsigned)
BEGIN
set @answer = (select answer from users where uid=given_uid);
if @answer = given_answer then 
UPDATE users
SET pincode = new_pincode
WHERE uid =given_uid ;
end if ;
END$$
DELIMITER ;
 
 
-- insert into user entries

$$
delimiter ;
drop procedure insertintouserentries;
-- insert new user entry record
delimiter $$
create procedure insertIntoUserEntries(in given_UID int)
begin
    declare doubleEntry bool;
    if ((select userExits.exitTime from userEntries 
    left join userExits 
    on userExits.userEntryID = userEntries.userEntryID
    where userEntries.UID = given_UID
    order by userEntries.entryTime desc limit 1) is null and given_uid in 
    (select uid from userentries)) then
        select 'user already in compound';
    else 
        insert into userEntries (UID, entryTime) values (given_UID, NOW());
        select userEntryID from userEntries
        order by userEntryID desc limit 1;
    end if;
end;
$$
delimiter ;


 -- insert new vehicle entry record

delimiter $$
create procedure insertIntoVehicleEntries(in given_vehicleNo varchar(15), in given_userEntryID int)
begin
    declare doubleEntry bool;
    if ((select vehicleExits.exitTime from vehicleEntries 
    left join vehicleExits 
    on vehicleExits.vehicleEntryID = vehicleEntries.vehicleEntryID
    where vehicleEntries.vehicleNo = given_vehicleNo
    order by vehicleEntries.vehicleEntryID desc limit 1) is null and given_vehicleNo in 
    (select vehicleno from vehicleentries))then
        select 'vehicle already in compound';
    else 
        insert into vehicleEntries (vehicleNo, userEntryID) values (given_vehicleNo, given_userEntryID);
    end if;
end;
$$
delimiter ;


-- insert a user exit record
DELIMITER $$
create procedure insertIntoUserExits(in userEntryID2 int)
begin
    if((select userExits.exitTime from userEntries
    left join userExits 
    on userExits.userEntryID = userEntries.userEntryID
    where userEntries.userEntryID = userEntryID2
    order by userEntries.entryTime desc limit 1) is null ) then
        insert into userExits (userEntryID) values (userEntryID2) ;
        select userexitID from userExits order by userExitID desc limit 1;
    else 
        select 'not in the compound. cannot exit';
    end if;
end;
$$
delimiter

-- insert a vehicle exit record
delimiter $$
create procedure insertIntoVehicleExits(in vehicleEntryID2 int, in userExitID2 int)
begin
    if((select vehicleExits.exitTime from vehicleEntries
    left join vehicleExits 
    on vehicleExits.vehicleEntryID = vehicleEntries.vehicleEntryID
    where vehicleEntries.vehicleEntryID = vehicleEntryID2
    order by vehicleEntries.vehicleEntryID desc limit 1) is null) then
        insert into vehicleExits (vehicleEntryID, userExitID) values (vehicleEntryID2, userExitID2);
        select vehicleExitID from vehicleExits
        order by vehicleExitID desc limit 1;
    else 
        select 'vehicle already exited';
    end if;
end;
$$
delimiter ;


-- entry exit record of specific vehicle no
select * from vehicleentries left join vehicleexits on vehicleentries.vehicleentryid = vehicleexits.vehicleentryid ;

-- find busiest hour
 select hour(exittime) as hour_, count(*) from
 (SELECT userexitid, exittime  from userexits union 
SELECT userentryid,entrytime  from userentries)s
group by hour_ order by count(*) desc;


-- for report generation
select count(*) from vehicles;
select count(*) from users;
select type, count(*) from vehicles group by type;
select count(*) from userentries;
select count(*) from userexits;
select count(*) from userentries where date(entrytime)>=curdate();
select count(*) from userexits where date(exittime)>=curdate();
select count(*) from vehicleentries;
select count(*) from vehicleexits;




-- entry exit record of vehicles 
select vehicles.owner ,v8.vehicleno, v8.entrytime, v8.exittime, v8.user_entered ,
v8.user_exited from vehicles right join (
select v7.vehicleno, v7.entrytime,v7.exittime , v7.uid as user_entered_Uid, v7.who_entered as user_entered , v7.who_exited_uid as user_exited_Uid, 
users.name as user_exited from users right join ( select v6.vehicleentryid, v6.userentryid, v6.vehicleno, v6.vehicleexitid, v6.userexitid, 
v6.entrytime, v6.uid, v6.who_entered , v6.who_exited_entryid, userentries.uid as who_exited_uid , v6.exittime from userentries right join 
(select v5.vehicleentryid, v5.userentryid, v5.vehicleno, v5.vehicleexitid, v5.userexitid, v5.entrytime, v5.uid, v5.who_entered ,
userexits.userentryid as who_exited_entryid , userexits.exittime from userexits right join ( select  v4.vehicleentryid, v4.userentryid, 
v4.vehicleno, v4.vehicleexitid, v4.userexitid, v4.entrytime, v4.uid, users.name as who_entered from users right join (
select v3.vehicleentryid, v3.userentryid, v3.vehicleno, v3.vehicleexitid, v3.userexitid, userentries.entrytime, userentries.uid
from userentries right join (select v1.vehicleentryid, v1.userentryid, v1.vehicleno, v2.vehicleexitid, v2.userexitid 
from vehicleentries v1 left join vehicleexits v2 on v1.vehicleentryid = v2.vehicleentryid)v3 
on v3.userentryid = userentries.userentryid)v4 on v4.uid = users.uid)v5 on v5.userexitid = userexits.userexitid)v6 
on v6.who_exited_entryid = userentries.userentryid)v7 on v7.who_exited_uid = users.uid)v8 on v8.vehicleno = vehicles.vehicleno  ;

-- entry exit record of vehicles of all users
select s3.uid , s3.name,  s3.enteredIn , s3.entrytime, s3.exittime,  vehicleentries.vehicleno as exitedIn from vehicleentries right join(
select s2.uid , s2.name, s2.userentryid , s2.userexitid, s2.enteredIn , 
s2.vehicleentryid, s2.exittime, s2.entrytime, vehicleexits.vehicleexitid,vehicleexits.vehicleentryid as vehicleexitKaentryid
 from vehicleexits right join( select s1.uid , s1.name, s1.userentryid , s1.userexitid, vehicleentries.vehicleno as enteredIn , 
vehicleentries.vehicleentryid, s1.exittime, s1.entrytime
from vehicleentries right join (select users.Uid, name, userentryid, 
userexitid,entrytime, exittime from users join 
(select userentries.userentryid, uid, entrytime, userexitid,exittime from userentries left join userexits on 
userentries.userentryid = userexits.userentryid)s on users.uid = s.uid)s1 on vehicleentries.userentryid = s1.userentryid)s2
on vehicleexits.userexitid = s2.userexitid)s3 on vehicleentries.vehicleentryid = s3.vehicleexitKaentryid  ;



-- show the entrytime and exittime for all users
select users.name ,u3.uid ,u3.entrytime, u3.exittime from users right join (
select u1.uid ,u1.entrytime, u2.exittime from userentries u1 left join userexits u2 on 
u1.userentryid = u2.userentryid)u3 on u3.uid = users.uid;



-- checking entry and exit for a particular vehicle number 
set @vehicleNumber = 'MP18BF1485';
select s1.vehicleentryid,s1.entryTime, s2.exitTime 
from 
	(select userEntries.entryTime, vehicleEntries.vehicleNo, vehicleEntries.vehicleEntryID 
	from userEntries 
	join vehicleEntries on userEntries.userEntryID = vehicleEntries.userEntryID
	where vehicleEntries.vehicleNo = @vehicleNumber) as s1 
left join 
	(select vehicleExits.vehicleEntryID, userExits.exitTime 
	from vehicleExits 
	join userExits on vehicleExits.userExitID = userExits.userExitID) as s2
on s1.vehicleEntryID = s2.vehicleEntryID
order by s1.entryTime;


-- get vehicle records by pincode

delimiter $$
create procedure getRecordsByPincode(in pin int)
begin
select vehicleNo, EntryTime, ExitTime from
(select v3.vehicleno , v4.entrytime , v3.vehicleentryid from vehicleEntries v3 join userEntries v4 on v3.userentryid = v4.userentryid)s1 
left join (select v1.vehicleentryid, v2.exittime from vehicleExits v1 join userExits v2 on v1.userexitid=v2.userexitid)s2
on s1.vehicleEntryID = s2.vehicleEntryID
where vehicleNo in (select vehicleNo from
Users join Vehicles on vehicles.owner = users.UID
where pincode = pin);
end;
$$
delimiter ;
call getrecordsbypincode(333031);
