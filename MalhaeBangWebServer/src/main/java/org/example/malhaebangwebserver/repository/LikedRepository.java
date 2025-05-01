package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.Liked;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface LikedRepository extends JpaRepository<Liked, Integer> {

    @Query("SELECT l FROM Liked l JOIN FETCH l.house JOIN FETCH l.folder JOIN FETCH l.user WHERE l.user.userId = :userId")
    List<Liked> findAllByUser_UserId(@Param("userId") Integer userId);


}