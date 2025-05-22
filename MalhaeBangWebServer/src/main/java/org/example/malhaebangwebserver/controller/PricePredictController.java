package org.example.malhaebangwebserver.controller;


import org.springframework.ui.Model;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
public class PricePredictController {

    @GetMapping("/pricepredict")
    public String showPricePredict(Model model) {

        model.addAttribute("content", "pricepredict/pricepredict-index :: content");
        return "layout";
    }
}

