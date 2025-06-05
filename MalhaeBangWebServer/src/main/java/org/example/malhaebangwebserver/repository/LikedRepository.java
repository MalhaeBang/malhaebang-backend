package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.House;
import org.example.malhaebangwebserver.model.entity.Liked;
import org.example.malhaebangwebserver.model.entity.User;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;


import java.util.List;
import java.util.Optional;

public interface LikedRepository extends JpaRepository<Liked, Integer> {


    Optional<Liked> findByUserAndHouse(User user, House house);
    List<Liked> findByUser(User user);

    @Query("SELECT l FROM Liked l WHERE l.user.userEmail = :email ORDER BY l.likedAt DESC")
    List<Liked> findTop2ByUserEmailOrderByLikedAtDesc(@Param("email") String email, Pageable pageable);
}