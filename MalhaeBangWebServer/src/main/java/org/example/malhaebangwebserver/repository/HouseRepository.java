package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.dto.SimpleHouseDto;
import org.example.malhaebangwebserver.model.entity.House;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface HouseRepository extends JpaRepository<House, Integer> {
    @Query("SELECT new org.example.malhaebangwebserver.model.dto.SimpleHouseDto(h.latitude, h.longitude, h.title) FROM House h")
    List<SimpleHouseDto> findSimpleDtoAll();
}

