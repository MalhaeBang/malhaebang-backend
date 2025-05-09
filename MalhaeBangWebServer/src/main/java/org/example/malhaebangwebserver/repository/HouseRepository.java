package org.example.malhaebangwebserver.repository;

import org.example.malhaebangwebserver.model.entity.House;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface HouseRepository extends JpaRepository<House, Integer> {
}
