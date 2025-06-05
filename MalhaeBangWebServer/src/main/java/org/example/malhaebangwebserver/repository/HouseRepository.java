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
    @Query("SELECT new org.example.malhaebangwebserver.model.dto.SimpleHouseDto(" +
            "h.houseId, h.latitude, h.longitude, h.title, h.price, h.address, h.floor, " +
            "h.depositType, h.mfee, h.aFrom, h.agentComm, h.agentInfo, " +
            "h.roomsCount, h.options, h.postedAt, h.gu, h.dong, " +
            "h.imgUrl, h.areaSize, h.direction, h.builtDate, " +
            "h.parking, h.buildingType, h.houseFeature, h.houseExplanations, h.houseNum, h.safetyGrade) " +
            "FROM House h " +
            "WHERE (:depositType IS NULL OR :depositType = '' OR h.depositType = :depositType) " +
            "AND (:safetyGrade IS NULL OR :safetyGrade = '' OR h.safetyGrade = :safetyGrade) " +
            "AND (:minPrice IS NULL OR :maxPrice IS NULL OR " +
            "   (h.depositType = '전세' AND h.deposit BETWEEN :minPrice AND :maxPrice) OR " +
            "   (h.depositType = '월세' AND h.monthlyRent BETWEEN :minPrice AND :maxPrice)) " +
            "AND (:gu IS NULL OR :gu = '' OR h.gu = :gu) " +
            "AND (:dong IS NULL OR :dong = '' OR h.dong = :dong)")
    List<SimpleHouseDto> findSimpleDtoByFilters(@Param("depositType") String depositType,
                                                @Param("safetyGrade") String safetyGrade,
                                                @Param("minPrice") Integer minPrice,
                                                @Param("maxPrice") Integer maxPrice,
                                                @Param("gu") String gu,
                                                @Param("dong") String dong);


//   지도 필터 드롭다운용

    @Query("SELECT DISTINCT h.depositType FROM House h")
    List<String> findDistinctDepositTypes();

    @Query("SELECT DISTINCT h.safetyGrade FROM House h ORDER BY CASE h.safetyGrade " +
           "WHEN '매우안전' THEN 1 " +
           "WHEN '안전' THEN 2 " +
           "WHEN '보통' THEN 3 " +
           "WHEN '주의' THEN 4 " +
           "WHEN '위험' THEN 5 " +
           "ELSE 6 END")
    List<String> findDistinctSafetyGrades();

    @Query("SELECT DISTINCT h.direction FROM House h")
    List<String> findDistinctDirections();

    @Query("SELECT DISTINCT h.parking FROM House h")
    List<String> findDistinctParking();

    @Query("SELECT DISTINCT h.gu FROM House h")
    List<String> findDistinctGu();

    @Query("SELECT DISTINCT h.dong FROM House h WHERE h.gu = :gu")
    List<String> findDistinctDongByGu(@Param("gu") String gu);

    @Query("SELECT COUNT(h) FROM House h WHERE h.gu IS NOT NULL")
    long countSeoulHouses();

    // main 평균수치 
    @Query("SELECT COUNT(h) FROM House h WHERE h.depositType = '전세'")
    long countJeonse();

    @Query("SELECT COUNT(h) FROM House h WHERE h.depositType = '월세' ")
    long countWolse();

    @Query("SELECT AVG(h.deposit) FROM House h WHERE h.depositType = '전세' ")
    Double avgJeonseDeposit();
    
    @Query("SELECT AVG(h.monthlyRent) FROM House h WHERE h.depositType = '월세'")
    Double avgWolseRent();

    @Query("SELECT new org.example.malhaebangwebserver.model.dto.SimpleHouseDto(" +
           "h.houseId, h.latitude, h.longitude, h.title, h.price, h.address, h.floor, " +
           "h.depositType, h.mfee, h.aFrom, h.agentComm, h.agentInfo, " +
           "h.roomsCount, h.options, h.postedAt, h.gu, h.dong, " +
           "h.imgUrl, h.areaSize, h.direction, h.builtDate, " +
           "h.parking, h.buildingType, h.houseFeature, h.houseExplanations, h.houseNum, h.safetyGrade) " +
           "FROM House h " +
           "WHERE h.houseId = :houseId")
    SimpleHouseDto findSimpleDtoById(@Param("houseId") Integer houseId);
}

