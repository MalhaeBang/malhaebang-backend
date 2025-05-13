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
    @Query("SELECT new org.example.malhaebangwebserver.model.dto.SimpleHouseDto(h.latitude, h.longitude, h.address) " +
            "FROM House h " +
            "WHERE (:depositType IS NULL OR :depositType = '' OR h.depositType = :depositType) " +
            "AND (:direction IS NULL OR :direction = '' OR h.direction = :direction) " +
            "AND (:parking IS NULL OR :parking = '' OR h.parking = :parking) " +
            "AND (:gu IS NULL OR :gu = '' OR h.gu = :gu) " +
            "AND (:dong IS NULL OR :dong = '' OR h.dong = :dong)")
    List<SimpleHouseDto> findSimpleDtoByFilters(@Param("depositType") String depositType,
                                                @Param("direction") String direction,
                                                @Param("parking") String parking,
                                                @Param("gu") String gu,
                                                @Param("dong") String dong);


//   지도 필터 드롭다운용

    @Query("SELECT DISTINCT h.depositType FROM House h")
    List<String> findDistinctDepositTypes();

    @Query("SELECT DISTINCT h.direction FROM House h")
    List<String> findDistinctDirections();

    @Query("SELECT DISTINCT h.parking FROM House h")
    List<String> findDistinctParking();

    @Query("SELECT DISTINCT h.gu FROM House h")
    List<String> findDistinctGu();

    @Query("SELECT DISTINCT h.dong FROM House h WHERE h.gu = :gu")
    List<String> findDistinctDongByGu(@Param("gu") String gu);

}

