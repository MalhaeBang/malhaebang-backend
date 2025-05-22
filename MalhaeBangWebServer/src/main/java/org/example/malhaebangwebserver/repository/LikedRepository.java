package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.House;
import org.example.malhaebangwebserver.model.entity.Liked;
import org.example.malhaebangwebserver.model.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;


import java.util.List;
import java.util.Optional;

public interface LikedRepository extends JpaRepository<Liked, Integer> {


    Optional<Liked> findByUserAndHouse(User user, House house);
    List<Liked> findByUser(User user);

}